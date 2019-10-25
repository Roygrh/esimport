from datetime import datetime
from datetime import timedelta
from datetime import timezone

from esimport.mappings.account import AccountMapping
from esimport.tests_new2.base_fixutres import *
from esimport.tests_new2.test_helpers import fetch_sqs_messages
from esimport.tests_new2.test_helpers import sqs_msg_parser


class TestAccountMapping:
    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_accounts_in_period(self, latest_ids_table, sqs_q):
        am = AccountMapping()
        am.setup()

        am.process_accounts_in_period("2019-01-01", "2019-01-02")

        # messages in sqs are not instantly available
        messages = fetch_sqs_messages(sqs_q)
        assert len(messages[0].body.split("\n")) == 8

    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_accounts_sequence_maintained(self, latest_ids_table, sqs_q):
        am = AccountMapping()
        am.setup()

        new_start_date = am.process_accounts_in_period("2019-01-01", "2019-01-02")
        messages = fetch_sqs_messages(sqs_q)
        parsed_sqs_msgs = sqs_msg_parser(messages[0].body)
        import pdb
        pdb.set_trace()
        last_previous_msg = parsed_sqs_msgs[-1]

        new_start_date2 = am.process_accounts_in_period(new_start_date, new_start_date + timedelta(days=1))
        messages = fetch_sqs_messages(sqs_q)
        parsed_sqs_msgs2 = sqs_msg_parser(messages[0].body)
        first_current_msg = parsed_sqs_msgs2[0]

        # This tests is different from others because `am.process_accounts_in_period(start_date, end_date)`
        # that has difference between dates arguments only one day, will select all records that has date < end_date
        # and return `new_start_date` that will be equal `start_date` argument.
        # To check that dates increased checking `new_start_date2` variable
        assert first_current_msg["_id"] == last_previous_msg["_id"]
        assert new_start_date2 - new_start_date == timedelta(days=1)


    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_accounts_from_id(self, latest_ids_table, sqs_q):
        am = AccountMapping()
        am.setup()

        result = am.process_accounts_from_id(
            next_id_to_process=0, start_date="2019-01-01"
        )
        # messages in sqs are not instantly available
        messages = fetch_sqs_messages(sqs_q)
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
