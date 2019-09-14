################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import logging
import time
from datetime import datetime, timedelta, timezone

from dateutil import parser

from esimport import settings
from esimport.mappings.appended_doc import PropertyAppendedDocumentMapping
from esimport.models.account import Account
from esimport.utils import convert_utc_to_local_time, set_utc_timezone

logger = logging.getLogger(__name__)


class AccountMapping(PropertyAppendedDocumentMapping):
    dates_to_localize = (
        ('Created', 'CreatedLocal'),
        ('Activated', 'ActivatedLocal'))

    def __init__(self):
        super(AccountMapping, self).__init__()
        self.time_delta_window = timedelta(minutes=10)
        self.default_query_limit = 20

    def setup(self):  # pragma: no cover
        super(AccountMapping, self).setup()
        self.model = Account(self.conn)
        self._version_date_fieldname = self.model._version_date_fieldname

    @staticmethod
    def get_monitoring_metric():
        return settings.DATADOG_ACCOUNT_METRIC

    def get_initial_start_end_dates(self, start_date) -> (datetime, datetime):
        if start_date and start_date != '1900-01-01':
            start_date = parser.parse(start_date)
        else:
            # otherwise, get the most recent starting point from data in DynamoDB
            # using the same date field that is used fro versioning
            start_date = parser.parse(self.latest_date())
            logger.info("Data Check - Created: {0}".format(start_date))

        assert start_date is not None, "Start Date is null.  Unable to sync accounts."

        start_date = set_utc_timezone(start_date)
        end_date = start_date + self.time_delta_window

        return start_date, end_date

    def update_start_end_dates(self, latest_processed_date: datetime, end_date: datetime) -> (datetime, datetime):
        # advance start date but never beyond the last end date
        start_date = min(latest_processed_date, end_date)

        # advance end date until reaching now
        end_date = min(end_date + self.time_delta_window, datetime.now(timezone.utc))
        return start_date, end_date

    def process_accounts_in_period(self, start_date, end_date):
        new_start_date = start_date
        count = 0
        logger.info("Checking for new and updated accounts between {0} and {1}".format(start_date, end_date))

        for account in self.model.get_accounts_by_modified_date(start_date, end_date):
            count += 1
            self.append_site_values(account)
            logger.debug("Record found: {0}".format(account.get('ID')))

            # keep track of latest start_date (query is ordering DateModifiedUTC ascending)
            new_start_date = account.get('DateModifiedUTC')
            logger.debug("New Start Date: {0}".format(new_start_date))

            self.add(account.es(), new_start_date)

        # send the remainder of accounts to elasticsearch
        self.add(None, new_start_date)

        logger.info("Processed a total of {0} accounts".format(count))
        return new_start_date

    def process_accounts_from_id(self, latest_processed_id: int, start_date) -> int:
        """

        :param latest_processed_id: id in MSSQL from which query accounts should be processed
        :param start_date:
        :return:
        """
        created_date = None
        for account in self.model.get_accounts_by_created_date(latest_processed_id, self.default_query_limit, start_date):
            self.append_site_values(account)
            latest_processed_id = account.get('ID')
            created_date = account.get('Created')
            self.add(account.es())
            logger.info("Updating Account ID: {0} and Date_Created_UTC: {1}".format(latest_processed_id, created_date))

        # for cases when all/remaining items count were less than limit
        self.add(None)
        return latest_processed_id

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
    Update Account records in Elasticsearch
    """
    def update(self, start_date):
        latest_processed_id = 0
        max_id = self.max_id()
        while latest_processed_id < max_id:
            latest_processed_id = self.process_accounts_from_id(latest_processed_id, start_date)


    """
    Loop to continuous add/update accounts
    """
    def sync(self, start_date):
        start_date, end_date = self.get_initial_start_end_dates(start_date)
        while True:
            latest_processed_date = self.process_accounts_in_period(start_date, end_date)

            logger.info("[Delay] Reset SQL connection and waiting {0} seconds".format(self.db_wait))
            self.model.conn.reset()
            time.sleep(self.db_wait)

            start_date, end_date = self.update_start_end_dates(latest_processed_date, end_date)

