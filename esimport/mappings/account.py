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
from datetime import datetime, timedelta, timezone
from dateutil import parser
from operator import itemgetter

from elasticsearch import exceptions
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from esimport.connectors.mssql import MsSQLConnector
from esimport.models.base import BaseModel
from esimport import settings
from esimport.utils import retry
from esimport.utils import convert_utc_to_local_time, set_utc_timezone
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

    @staticmethod
    def get_monitoring_metric():
        return settings.DATADOG_ACCOUNT_METRIC

    """
    Loop to continuous add/update accounts
    """
    def sync(self, start_date):
        if start_date and start_date != '1900-01-01':
            start_date = parser.parse(start_date)
        else:
            # otherwise, get the most recent starting point from data in Elasticsearch (use Created to prevent gaps in data)
            start_date = self.get_most_recent_date('Created', Account.get_type())
            logger.info("Data Check - Created: {0}".format(start_date))

        assert start_date is not None, "Start Date is null.  Unable to sync accounts."

        start_date = set_utc_timezone(start_date)

        time_delta_window = timedelta(minutes=10)
        end_date = start_date + time_delta_window

        while True:
            count = 0
            logger.info("Checking for new and updated accounts between {0} and {1}".format(start_date, end_date))

            for account in self.model.get_accounts_by_modified_date(start_date, end_date):
                count += 1
                self.append_site_values(account)
                logger.debug("Record found: {0}".format(account.get('ID')))

                # keep track of latest start_date (query is ordering DateModifiedUTC ascending)
                start_date = account.get('DateModifiedUTC')
                logger.debug("New Start Date: {0}".format(start_date))

                self.add(account.es(), self.step_size, start_date)

            # send the remainder of accounts to elasticsearch 
            self.add(None, 0, start_date)

            logger.info("Processed a total of {0} accounts".format(count))
            logger.info("[Delay] Reset SQL connection and waiting {0} seconds".format(self.db_wait))

            self.model.conn.reset()
            time.sleep(self.db_wait)

            # advance start date but never beyond the last end date
            start_date = min(start_date, end_date)

            # advance end date until reaching now
            end_date = min(end_date + time_delta_window, datetime.now(timezone.utc))

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
    Update Account records in Elasticsearch
    """
    def update(self, start_date):
        start = 0
        created_date = None
        max_id = self.max_id()
        while start < max_id:
            for account in self.model.get_accounts_by_created_date(start, self.step_size, start_date):
                self.append_site_values(account)
                account_es = account.es()
                start = account.get('ID')
                created_date = account.get('Created')
                self.add(account_es, self.step_size)

            logger.info("Updating Account ID: {0} and Date_Created_UTC: {1}".format(start, created_date))

            # for cases when all/remaining items count were less than limit
            self.add(None, min(len(self._items), self.step_size))

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
