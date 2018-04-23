################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################



import sys
import traceback
import time
import logging
import threading

from datetime import datetime
from dateutil import parser
from operator import itemgetter

from elasticsearch import exceptions
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from esimport.connectors.mssql import MsSQLConnector
from esimport.models.base import BaseModel
from esimport import settings
from esimport.utils import retry
from esimport.utils import convert_utc_to_local_time
from esimport.models import ESRecord
from esimport.models.account import Account
from esimport.mappings.appended_doc import PropertyAppendedDocumentMapping

from extensions import sentry_client

logger = logging.getLogger(__name__)

class AccountMapping(PropertyAppendedDocumentMapping):
    dates_to_localize = (
        ('Created', 'CreatedLocal'),
        ('Activated', 'ActivatedLocal'))

    def __init__(self):
        super(AccountMapping, self).__init__()

    def setup(self):  # pragma: no cover
        super(AccountMapping, self).setup()
        self.model = Account(self.conn)

    # Need this for tests
    def add_accounts(self, start_date):
        count = 0
        start = self.max_id() + 1
        logger.debug("Get Accounts from {0} to {1} since {2}"
                     .format(start, start + self.step_size, start_date))
        for account in self.model.get_accounts_by_created_date(start, self.step_size, start_date):
            count += 1

            _action = super(AccountMapping, self).get_site_values(account.get('ServiceArea'))

            if 'TimeZone' in _action:
                for pfik, pfiv in self.dates_to_localize:
                    _action[pfiv] = convert_utc_to_local_time(account.record[pfik], _action['TimeZone'])

            account.update(_action)
            rec = account.es()
            logger.debug("Record found: {0}".format(account.get('ID')))
            self.add(rec, self.step_size)

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))

        # only wait between DB calls when there is no delay from ES (HTTP requests)
        if count <= 0:
            self.model.conn.reset()
            logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
            time.sleep(self.db_wait)

    """
    Loop to continuous add accounts
    """
    def sync(self, start_date):
        while True:
            self.add_accounts(start_date)

    
    """
    Get last record modified time from elasticsearch
    """
    def get_initial_time(self):
        q = {
            "query": {
                "match_all": {}
            },
            "sort": [
                {
                    "DateModifiedUTC": {
                        "order": "desc",
                        "mode": "max",
                        "unmapped_type": "date"
                    }
                }
            ],
            "size": 1
        }

        hits = self.es.search(index=settings.ES_INDEX, 
                              doc_type=Account.get_type(), body=q)['hits']['hits']

        try:
            # return 1/1/2000 just to re-process older modified account records.
            initial_time = datetime(2000, 1, 1)
            #initial_time = parser.parse(hits[0]['_source']['DateModifiedUTC'])
        except Exception as err:
            initial_time = datetime(2000, 1, 1)
            logger.error(err)
            traceback.print_exc(file=sys.stdout)
            sentry_client.captureException()

        return initial_time


    def check_for_time_change(self):
        initial_time = self.get_initial_time()

        while True:
            logger.debug("Checking for accounts updated since {0}".format(initial_time))

            check_update = self.model.get_updated_records_query(self.step_size, initial_time)
            updated = [u for u in check_update]
            logger.debug("Found {0} updated account records".format(len(updated)))

            if len(updated) > 0:
                initial_time = max(updated, key=itemgetter(1))[1]
                zpa_ids = [str(id[0]) for id in updated]
                accounts = self.model.get_accounts_by_id(zpa_ids)
                actions = [account.es() for account in accounts]
                logger.debug("Sending {0} actions to Elasticsearch".format(len(actions)))
                self.bulk_add_or_update(self.es, actions)
            else:
                # sleep before checking for new updates
                self.model.conn.reset()
                logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
                time.sleep(self.db_wait)

    """
    Get existing accounts from ElasticSearch
    """
    @retry(settings.ES_RETRIES, settings.ES_RETRIES_WAIT, retry_exception=exceptions.ConnectionError)
    def get_existing_accounts(self, start_zpa_id, limit):
        logger.debug("Fetching {0} records from ES where ID >= {1}" \
                     .format(limit, start_zpa_id))
        records = self.es.search(index=settings.ES_INDEX, doc_type=Account.get_type(),
                                 sort="ID:asc", size=limit,
                                 q="ID:[{0} TO *]".format(start_zpa_id))
        for record in records['hits']['hits']:
            yield record.get('_source')

    """
    Get records from MSSQL based on records from ElasticSearch
    """
    def get_new_and_existing_accounts_tuples(self, start, limit):
        ids = []
        accounts = []
        for account in self.get_existing_accounts(start, limit):
            accounts.append(account)
            ids.append(str(account.get('ID')))

        for row in self.model.get_records_by_zpa_id(ids):
            logger.debug("Record found: {0}".format(row.get('ID')))
            # only for account where there are 1 or more missing property fields
            if any([pfik not in row for pfik, pfiv in self.property_fields_include]):
                new_property_fields_include = [(pfik, pfiv) for pfik, pfiv in self.property_fields_include
                                               if pfik not in row]
                # get some properties from PropertyMapping
                _action = {}
                for properte in self.pm.get_properties_by_service_area(row.get('ServiceArea')):
                    for pfik, pfiv in new_property_fields_include:
                        _action[pfik] = properte.get(pfiv or pfik, "")
                    break
                row.update(_action)
            es_records = filter(lambda x: x if x.get('ID') == row.get('ID') else [None], accounts)
            if not isinstance(es_records, list):
                es_records = list(es_records)
            if es_records:
                account = (row, es_records[0])
                yield account

    """
    Filter records based on new fields found in MSSQL but not in ElasticSearch
    """
    def get_updated_records(self, start, limit):
        ignore_fields = ['Price', 'Currency']

        for new, current in self.get_new_and_existing_accounts_tuples(start, limit):
            new_fields = set(new.keys()) - set(current.keys()) - set(ignore_fields)
            new_record = dict([(k, v) for k, v in new.items() if k in new_fields])
            if len(new_record) > 0:
                new_account = ESRecord(new_record, Account.get_type()) \
                    .es(record_id=new.get('ID'))
                yield new_account

    """
    DO NOT CALL! We don't want this functionality currently.
    """
    def update(self):
        start = 0
        total = self.get_es_count()
        while start < total:
            count = 0
            for account in self.get_updated_records(start, self.step_size):
                count += 1
                start = account.get('_id')  # because account is dict() not ESRecord
                self.add(account, self.step_size)
                if settings.LOG_LEVEL == logging.DEBUG:  # pragma: no cover
                    logger.debug("Updating Account: {0}".format(self.pp.pformat(account)))
            start += 1
            total = self.get_es_count()

            # for cases when all/remaining items count were less than limit
            self.add(None, min(len(self._items), self.step_size))

            # only wait between DB calls when there is no delay from ES (HTTP requests)
            if count <= 0:
                logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
                time.sleep(self.db_wait)

    """
    NON FUNCTIONAL. Needs to be implemented.
    """
    def backload(self, start_date):
        start = 0
        for account in self.model.get_accounts_by_created_date(start, self.step_size, start_date):
            acc = account.es()
            logger.debug("Record found: {0}".format(account.get('ID')))
            self.add(dict(acc), self.step_size)
            start = account.get('ID') + 1

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))
