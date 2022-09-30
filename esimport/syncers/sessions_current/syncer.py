import time
from datetime import datetime, timezone

from esimport.core import PropertiesMixin, Record, SyncBase

from ._queries import SESSIONS_QUERY
from ._schema import SessionSchema
import logging


class SessionsCurrentSyncer(SyncBase, PropertiesMixin):

    target_elasticsearch_index_prefix: str = "sessions"
    uses_date_partitioned_index: bool = True

    # How the data going to look like?
    # Just take a look at `_schema.py` file
    incoming_data_schema = SessionSchema

    default_query_limit: int = 500

    # the field to consider its value as the record _date (and even a version)
    # it has to be a field holding a datetime object
    record_date_fieldname: str = "LogoutTime"

    # the type of the record for Elasticsearch
    record_type = "session"

    cursor_name = "sessions_current"

    date_fields_to_localize = (
        ("LoginTime", "LoginTimeLocal"),
        ("LogoutTime", "LogoutTimeLocal"),
    )

    def get_sessions(
        self, start_id, limit, start_date="1900-01-01", use_historical=True
    ):
        query = self._get_sessions_query(use_historical)

        for row in self.fetch_rows_as_dict(query, limit, start_id, start_id, limit):
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = self.set_utc_timezone(value)

            record_date = row[self.record_date_fieldname]

            yield Record(
                _index=self.get_target_elasticsearch_index(record_date),
                _type=self.record_type,
                _source=row,
                _date=record_date,
            )

    @staticmethod
    def _get_sessions_query(use_historical: bool) -> str:
        # Session data older than 15 minutes lives in the Radius_Accounting_Event_History table.
        # Real-time session data (less than 24 hours old) lives in the Radius_Accounting_Event table.
        event_table = "Radius_Accounting_Event_History" if use_historical else "Radius_Accounting_Event"
        event_table_id = "Radius_Accounting_Event_ID" if use_historical else "ID"
        return SESSIONS_QUERY.format(event_table, event_table_id)

    def resume(
        self, from_id: int, start_date, use_historical: bool
    ) -> (int, int, datetime):

        most_recent_session_time = datetime.now(timezone.utc)
        count = 0
        to_id = from_id + self.default_query_limit

        self.debug(f"Getting sessions from {from_id} to {to_id} since {start_date}")

        for session_record in self.get_sessions(
            from_id, self.default_query_limit, start_date, use_historical
        ):
            self.report_old_record(session_record)
            count += 1
            session_id = session_record.raw.get("ID")
            # Distinguish normal (DB originated) sessions from PPK sessions in Elasticsearch
            # as we need to filter on 'is_ppk' for different reasons (e.g. alerting, debugging.. )
            session_record.raw.update({"is_ppk": False})
            self.debug(f"Record found: {session_id}")

            self.append_site_values(
                session_record,
                session_record.raw.get("ServiceArea"),
                self.date_fields_to_localize,
            )

            most_recent_session_time = session_record.raw[self.record_date_fieldname]
            self.add_record(session_record, cursor_name=self.cursor_name)
            from_id = session_record.raw.get("ID") + 1

        return count, from_id, most_recent_session_time

    def should_use_historical(
        self, count: int, last_known_time: datetime, was_historical: bool
    ) -> bool:
        # While we're catching up to the current time, use the historical session data source.
        # Once we're within an hour or there are no records being returned, then
        # switch to the real-time data source.
        now = datetime.now(timezone.utc)
        minutes_behind = (now - last_known_time).total_seconds() / 60

        if count == 0:
            switch_to_historical = False

        switch_to_historical = minutes_behind >= 60

        if switch_to_historical and not was_historical:
            self.info(
                f"Switching to use the historical session data source. Record Count: {count}, Minutes Behind: {minutes_behind}"
            )

        if not switch_to_historical and was_historical:
            self.info(
                f"Switching to use the real-time session data source. Record Count: {count}, Minutes Behind: {minutes_behind}"
            )

        return switch_to_historical

    def sync(self, start_date: datetime = None):
        assert start_date is not None, "start_date must be specified"

        use_historical = True
        next_id_to_process = self.max_id() + 1
        timer_start = time.time()

        while True:
            count, next_id_to_process, most_recent_session_time = self.resume(
                next_id_to_process, start_date, use_historical
            )

            elapsed_time = int(time.time() - timer_start)
            use_historical = self.should_use_historical(
                count, most_recent_session_time, use_historical
            )

            # habitually reset mssql connection.
            if count == 0 or elapsed_time >= self.database_connection_reset_limit:
                wait = self.db_wait
                self.info(f"[Delay] Reset SQL connection and waiting {wait} seconds")
                self.mssql.reset()
                self.sleep(wait)
                timer_start = time.time()  # reset timer

    ## Overrides
    @property
    def last_inserted_cursor_state(self):
        return self.dynamodb_table.get_item(
            Key={"doctype": self.cursor_name}, ConsistentRead=True
        )
