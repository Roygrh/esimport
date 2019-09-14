from datetime import datetime
from datetime import timezone
from datetime import timedelta
from time import sleep

from esimport.mappings.account import AccountMapping
from esimport.tests_new2.base_fixutres import *


class TestAccountMapping:
    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_accounts_in_period(self, latest_ids_table, sqs_q):
        am = AccountMapping()
        am.setup()

        result = am.process_accounts_in_period("1900-01-01", "2020-01-01")

        # messages in sqs are not instantly available
        messages = None
        for _ in range(15):
            messages = sqs_q.receive_messages()
            if messages:
                break

            sleep(1)

        assert messages is not None
        assert len(messages[0].body.split("\n")) == 40
        # TODO update fixtures and check that order is keept

    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_accounts_from_id(self, latest_ids_table, sqs_q):
        am = AccountMapping()
        am.setup()

        result = am.process_accounts_from_id(
            latest_processed_id=0, start_date="1900-01-01"
        )
        # messages in sqs are not instantly available
        messages = None
        for _ in range(15):
            messages = sqs_q.receive_messages()
            if messages:
                break

            sleep(1)

        assert messages is not None
        assert len(messages[0].body.split("\n")) == am.default_query_limit

    @pytest.mark.usefixtures("empty_table")
    def test_get_initial_start_end_dates(self, latest_ids_table):
        am = AccountMapping()
        am.setup()

        start_date, end_date = am.get_initial_start_end_dates("2019-01-01")
        assert start_date == datetime(2019, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert end_date == datetime(2019, 1, 1, 0, 10, 0, tzinfo=timezone.utc)

        latest_ids_table.put_item(
            Item={
                "doctype": am.model._type,
                "latest_id": 999,
                "latest_date": datetime(
                    2019, 1, 1, 1, 2, 3, tzinfo=timezone.utc
                ).isoformat(),
            }
        )

        start_date, end_date = am.get_initial_start_end_dates("1900-01-01")

        assert start_date == datetime(2019, 1, 1, 1, 2, 3, tzinfo=timezone.utc)
        assert end_date == datetime(
            2019, 1, 1, 1, 2, 3, tzinfo=timezone.utc
        ) + timedelta(minutes=10)

        start_date, end_date = am.get_initial_start_end_dates(None)

        assert start_date == datetime(2019, 1, 1, 1, 2, 3, tzinfo=timezone.utc)
        assert end_date == datetime(
            2019, 1, 1, 1, 2, 3, tzinfo=timezone.utc
        ) + timedelta(minutes=10)

    def test_update_start_end_dates(self):
        am = AccountMapping()
        am.setup()

        input_start_date = datetime(2019, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        input_end_date = datetime(2019, 1, 1, 0, 10, 0, tzinfo=timezone.utc)

        new_start_date, new_end_date = am.update_start_end_dates(
            latest_processed_date=input_start_date, end_date=input_end_date
        )

        assert input_start_date == new_start_date
        assert new_end_date == input_end_date + timedelta(minutes=10)

        # input_start_date is bigger than end_date

        input_start_date = datetime(2019, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        input_end_date = datetime(2019, 1, 1, 0, 10, 0, tzinfo=timezone.utc)

        new_start_date, new_end_date = am.update_start_end_dates(
            latest_processed_date=input_start_date, end_date=input_end_date
        )

        assert new_start_date == input_end_date
        assert new_end_date == input_end_date + timedelta(minutes=10)

        # end_date is bigger than now
        # if end_date is bigger than `update_start_end_dates()` should return `now` for end_date
        # it is impossible to test now values, so using approximation
        # returned value should not have big difference with now, assuming lest than 2 seconds

        input_start_date = datetime(2019, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        input_end_date = datetime.now(tz=timezone.utc)

        new_start_date, new_end_date = am.update_start_end_dates(
            latest_processed_date=input_start_date, end_date=input_end_date
        )

        assert new_start_date == new_start_date
        difference = datetime.now(tz=timezone.utc) - new_end_date
        assert difference.total_seconds() < 2
