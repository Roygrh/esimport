import time
from datetime import datetime, timezone
from typing import Generator

from esimport.core import PropertiesMixin, Record, SyncBase

from ._queries import GET_CONFERENCE_ADDITIONAL_ACCESS_CODES, GET_CONFERENCES_QUERY
from ._schema import ConferenceSchema


class ConferencesSyncer(SyncBase, PropertiesMixin):

    target_elasticsearch_index_prefix: str = "conferences"
    uses_date_partitioned_index: bool = False

    # How the data going to look like?
    # Just take a look at `_schema.py` file
    incoming_data_schema = ConferenceSchema

    default_query_limit: int = 50

    # the field to consider its value as the record _date (and even a version)
    # it has to be a field holding a datetime object
    record_date_fieldname: str = "UpdateTime"

    # the type of the record for Elasticsearch
    record_type = "conference"

    dates_to_localize = (
        ("DateCreatedUTC", "DateCreatedLocal"),
        ("StartDateUTC", "StartDateLocal"),
        ("EndDateUTC", "EndDateLocal"),
    )

    conference_columns_to_fetch = [
        "ID",
        "Name",
        "DateCreatedUTC",
        "ServiceArea",
        "Code",
        "MemberID",
        "MemberNumber",
        "MemberStatus",
        "SSID",
        "StartDateUTC",
        "EndDateUTC",
        "ConnectionLimit",
        "DownKbs",
        "UpKbs",
        "UserCount",
        "TotalInputBytes",
        "TotalOutputBytes",
        "TotalSessionTime",
        "GroupBandwidthLimit",
    ]

    def process_conferences_from_id(
        self, next_id: int, start_date: datetime
    ) -> (int, int):
        """
        :param next_id:
        :param start_date: - not the main criterion for querying records, only used to limit  timespan of processing.
        In consequent calls that parameter usually should be the same.
        :return:
        """
        count = 0
        for conference in self.get_conferences(
            next_id, self.default_query_limit, start_date
        ):
            count += 1
            self.debug(f"Record found: {conference.id}")

            self.update_time_zones(
                conference, conference.raw.get("ServiceArea"), self.dates_to_localize
            )
            self.add_record(conference)
            next_id = conference.id + 1

        return count, next_id

    def sync(self, start_date: datetime):
        """
        Continuously update ElasticSearch to have the latest Conference data
        """
        next_id_to_process = 0
        timer_start = time.time()
        while True:
            count, next_id_to_process = self.process_conferences_from_id(
                next_id_to_process, start_date=start_date
            )

            # always wait between DB calls
            time.sleep(self.db_wait)

            elapsed_time = int(time.time() - timer_start)

            # habitually reset mssql connections.
            if count == 0 or elapsed_time >= self.database_connection_reset_limit:
                wait = self.db_wait * 4
                self.info(f"[Delay] Reset SQL connection and waiting {wait} seconds")
                self.mssql.reset()
                time.sleep(wait)
                timer_start = time.time()  # reset timer
                # start over again when all records have been processed
                if count == 0:
                    next_id_to_process = 0

    def get_conferences(self, start, limit, start_date="1900-01-01"):
        self.debug(
            f"Fetching conferences from Scheduled_Access.ID >= {start} "
            f"AND Scheduled_Access.Date_Created_UTC > {start_date} (limit: {limit})"
        )

        for conference in self.fetch_rows(
            GET_CONFERENCES_QUERY,
            limit,
            start,
            start_date,
            column_names=self.conference_columns_to_fetch,
        ):
            # set all datetime objects to utc timezone
            for key, value in conference.items():
                if isinstance(value, datetime):
                    conference[key] = self.set_utc_timezone(value)

            conference["UpdateTime"] = datetime.now(timezone.utc)

            # Update the CodeList with the main Code first
            code_list = [conference.get("Code")]

            # Update the MemberNumberList with the main MemberNumber first
            member_number_list = [conference.get("MemberNumber")]

            # Initialize AccessCodes with the main memberID and member number
            access_codes_list = [
                {
                    "Code": conference.get("Code"),
                    "MemberNumber": conference.get("MemberNumber"),
                    "MemberID": conference.get("MemberID"),
                }
            ]

            for access_code in self.fetch_rows(
                GET_CONFERENCE_ADDITIONAL_ACCESS_CODES, conference["ID"]
            ):
                code_list.append(access_code.Code)
                member_number_list.append(access_code.MemberNumber)
                access_codes_list.append(
                    {
                        "Code": access_code.Code,
                        "MemberNumber": access_code.MemberNumber,
                        "MemberID": access_code.MemberID,
                    }
                )

            conference["CodeList"] = code_list
            conference["MemberNumberList"] = member_number_list
            conference["AccessCodes"] = access_codes_list

            record_date = conference[self.record_date_fieldname]
            yield Record(
                _index=self.get_target_elasticsearch_index(record_date),
                _type=self.record_type,
                _source=conference,
                _date=record_date,
            )
