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
from datetime import datetime, timedelta
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
from esimport.models.property import Property
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

    """
    Loop to continuous add/update accounts
    """
    def sync(self, start_date):

        # REVIEW: Only remove the TODO comment if it's actually done.  If I don't pass a date in, the code still defaults to 1/1/1900.  This is not the expected behavior.
        # TODO: Rework the code to look at the incoming start date.  If a valid start date is passed in we should use it, otherwise use the logic below.  
        #       Of course, the way it's setup currently it will always default to 1/1/1900, so this is the same as not passing in a date at all and in 
        #       that case, we should also use the logic below.

        # get the most recent starting point
        if start_date:
            start_date = parser.parse(start_date)
        else:
            start_date = self.get_most_recent_date('Created') # Don't start with last modified record just yet... min(self.get_most_recent_date('DateModifiedUTC'), self.get_most_recent_date('Created'))

        time_delta_window = timedelta(hours=1)
        end_date = start_date + time_delta_window

        while True:
            count = 0
            logger.info("Checking for new and updated accounts between {0} and {1}".format(start_date, end_date))

            for account in self.model.get_accounts_by_modified_date(start_date, end_date):
                count += 1
                self.append_site_values(account)
                logger.debug("Record found: {0}".format(account.get('ID')))
                self.add(account.es(), self.step_size)

                # keep track of latest start_date (query is ordering DateModifiedUTC ascending)
                start_date = parser.parse(account.get('DateModifiedUTC'))
                logger.debug("New Start Date: {0}".format(start_date))

            # send the remainder of accounts to elasticsearch 
            self.add(None, min(len(self._items), self.step_size))

            logger.info("Processed a total of {0} accounts".format(count))
            logger.info("[Delay] Waiting {0} seconds".format(self.db_wait))

            self.model.conn.reset()
            time.sleep(self.db_wait)

            # advance start date but never beyond the last end date
            start_date = min(start_date, end_date)

            # advance end date until reaching now
            end_date = min(end_date + time_delta_window, datetime.utcnow())


    """
    Get the most recent date requested from elasticsearch
    """
    def get_most_recent_date(self, date_field):
        q = {
                "query": {
                    "match_all": {}
                },
                "sort":[
                    {
                        str(date_field): {
                            "order": "desc",
                            "missing": "_last",
                            "unmapped_type": "date"
                        }
                    }
                ],
                "size": 1
        }

        try:
            hits = self.es.search(index=settings.ES_INDEX, doc_type=Account.get_type(), body=q)['hits']['hits']
            initial_time = parser.parse(hits[0]['_source'][date_field])
        except Exception as err:
            initial_time = datetime.utcnow()
            logger.error(err)
            traceback.print_exc(file=sys.stdout)
            sentry_client.captureException()

        return initial_time

    """
    Append site values to account record
    """
    def append_site_values(self, account):
        _action = super(AccountMapping, self).get_site_values(account.get('ServiceArea'))

        if 'TimeZone' in _action:
            for pfik, pfiv in self.dates_to_localize:
                _action[pfiv] = convert_utc_to_local_time(account.record[pfik], _action['TimeZone'])

        account.update(_action)


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
