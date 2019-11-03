import time
from datetime import datetime, timedelta, timezone
from typing import Generator

from dateutil import parser

from esimport.core import PropertiesMixin, Record, SyncBase

from ._queries import GET_ACCOUNTS_BY_ID, GET_ACCOUNTS_BY_MODIFIED_DATE
from ._schema import AccountSchema


class AccountsSyncer(SyncBase, PropertiesMixin):

    target_elasticsearch_index_prefix: str = "accounts"
    uses_date_partitioned_index: bool = False

    # How the data going to look like?
    # Just take a look at `_schema.py` file
    incoming_data_schema = AccountSchema

    default_query_limit: int = 20

    # the field to consider its value as the record _date (and even a version)
    # it has to be a field holding a datetime object
    record_date_fieldname: str = "DateModifiedUTC"

    # the type of the record for Elasticsearch
    record_type = "account"

    dates_to_localize = (("Created", "CreatedLocal"), ("Activated", "ActivatedLocal"))

    time_delta_window = timedelta(minutes=10)

    def get_initial_start_end_dates(self, start_date) -> (datetime, datetime):
        if start_date and start_date != "1900-01-01":
            start_date = parser.parse(start_date)
        else:
            # otherwise, get the most recent starting point from data in DynamoDB
            # using the same date field that is used fro versioning
            start_date = parser.parse(self.latest_date())
            self.info("Data Check - Created: {0}".format(start_date))

        assert start_date is not None, "Start Date is null.  Unable to sync accounts."

        start_date = self.set_utc_timezone(start_date)
        end_date = start_date + self.time_delta_window

        return start_date, end_date

    def update_start_end_dates(
        self, latest_processed_date: datetime, end_date: datetime
    ) -> (datetime, datetime):
        # advance start date but never beyond the last end date
        start_date = min(latest_processed_date, end_date)

        # advance end date until reaching now
        end_date = min(end_date + self.time_delta_window, datetime.now(timezone.utc))
        return start_date, end_date

    def process_accounts_in_period(self, start_date, end_date):
        new_start_date = start_date
        count = 0
        self.info(
            f"Checking for new/updated accounts between {start_date} and {end_date}"
        )

        for account in self.get_accounts_by_modified_date(start_date, end_date):
            count += 1
            self.append_site_values(account)
            self.debug("Record found: {0}".format(account.get("ID")))

            # keep track of latest start_date (query is ordering DateModifiedUTC ascending)
            new_start_date = account.get("DateModifiedUTC")
            self.debug("New Start Date: {0}".format(new_start_date))

            self.add_record(account)

        self.info("Processed a total of {0} accounts".format(count))
        return new_start_date

    def process_accounts_from_id(self, next_id_to_process: int, start_date) -> int:
        """
        :param next_id_to_process: id in MSSQL from which query accounts should be processed
        :param start_date:
        :return:
        """
        created_date = None
        for account in self.get_accounts_by_created_date(
            next_id_to_process, self.default_query_limit, start_date
        ):
            self.append_site_values(account)
            next_id_to_process = account.get("ID")
            created_date = account.get("Created")
            self.add_record(account)
            self.info(
                f"Updating Account ID: {next_id_to_process} and Date_Created_UTC: {created_date}"
            )

        return next_id_to_process

    def append_site_values(self, account: Record):
        """
        Append site values to account record
        """
        _action = self.get_site_values(account.raw.get("ServiceArea"))

        if "TimeZone" in _action:
            for pfik, pfiv in self.dates_to_localize:
                _action[pfiv] = self.convert_utc_to_local_time(
                    account.raw[pfik], _action["TimeZone"]
                )
        account.raw.update(_action)

    def update(self, start_date):
        """
        Update Account records in Elasticsearch
        """
        next_id_to_process = 0
        max_id = self.max_id()
        while next_id_to_process < max_id:
            next_id_to_process = self.process_accounts_from_id(
                next_id_to_process, start_date
            )

    def sync(self, start_date: datetime):
        """
        Loop to continuously add/update accounts
        """
        start_date, end_date = self.get_initial_start_end_dates(start_date)
        while True:
            latest_processed_date = self.process_accounts_in_period(
                start_date, end_date
            )

            self.info(
                f"[Delay] Reset SQL connection and waiting {self.db_wait} seconds"
            )
            self.mssql.reset()
            time.sleep(self.db_wait)

            start_date, end_date = self.update_start_end_dates(
                latest_processed_date, end_date
            )

    def get_accounts_by_created_date(self, start, limit, start_date="1900-01-01"):
        return self.get_accounts(GET_ACCOUNTS_BY_ID, limit, start, start_date)

    def get_accounts_by_modified_date(self, start_date, end_date):
        return self.get_accounts(
            GET_ACCOUNTS_BY_MODIFIED_DATE, start_date, end_date, start_date, end_date
        )

    def get_accounts(self, query, *args):
        for account in self.fetch_rows_as_dict(query, *args):
            account["Duration"] = self.find_duration(account)

            # Set all datetime objects to utc timezone
            for key, value in account.items():
                if isinstance(value, datetime):
                    account[key] = self.set_utc_timezone(value)

            record_date = account[self.record_date_fieldname]

            yield Record(
                _index=self.get_target_elasticsearch_index(record_date),
                _type=self.record_type,
                _source=account,
                _date=record_date,
            )

    @staticmethod
    def find_duration(account: dict):
        if account.get("ConsumableTime") is not None:
            return "{0} {1} {2}".format(
                account.get("ConsumableTime"),
                account.get("ConsumableUnit"),
                "consumable",
            )
        if account.get("SpanTime") is not None:
            return "{0} {1}".format(account.get("SpanTime"), account.get("SpanUnit"))

        return None
