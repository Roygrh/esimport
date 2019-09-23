from esimport.mappings.session import SessionMapping
from time import sleep
from esimport.tests_new2.base_fixutres import *
from esimport.tests_new2.test_helpers import sqs_msg_parser
from datetime import datetime
from datetime import timezone
from datetime import timedelta


class TestSessionMapping:
    @pytest.mark.usefixtures("empty_q", "empty_table")
    @pytest.mark.parametrize("use_historical", (False, True))
    def test_process_sessions_from_id(self, latest_ids_table, sqs_q, use_historical):
        sm = SessionMapping()
        sm.setup()
        sm.default_query_limit = 4

        table_name = "Radius.dbo.Radius_Stop_Event"
        next_id_to_process = sm.model.execute(
            f"Select MIN(ID) FROM {table_name}"
        ).fetchone()[0]

        sm.process_sessions_from_id(
            next_id_to_process=next_id_to_process,
            start_date="2019-01-01",
            use_historical=use_historical,
        )

        # messages in sqs are not instantly available
        messages = None
        for _ in range(15):
            messages = sqs_q.receive_messages()
            if messages:
                break

            sleep(1)

        assert messages is not None
        assert len(messages[0].body.split("\n")) == 4

    @pytest.mark.usefixtures("empty_q", "empty_table")
    @pytest.mark.parametrize("use_historical", (False, True))
    def test_process_sessions_sequence_maintained(
        self, latest_ids_table, sqs_q, use_historical
    ):
        """ Note that test expecte that `Radius_Event` and `Radius_Event_History` tables should have same ID counters.
        If this test is failing recreate this table or Radius database.
        :param latest_ids_table:
        :param sqs_q:
        :return:
        """

        sm = SessionMapping()
        sm.setup()
        sm.default_query_limit = 4

        table_name = "Radius.dbo.Radius_Stop_Event"
        next_id_to_process = sm.model.execute(
            f"Select MIN(ID) FROM {table_name}"
        ).fetchone()[0]

        count, next_id_to_process, most_recent_session_time = sm.process_sessions_from_id(
            next_id_to_process=next_id_to_process,
            start_date="2019-01-01",
            use_historical=use_historical,
        )

        # messages in sqs are not instantly available
        messages = None
        for _ in range(15):
            messages = sqs_q.receive_messages()
            if messages:
                break

            sleep(1)

        assert messages is not None
        parsed_sqs_msgs = sqs_msg_parser(messages[0].body)
        last_previous_msg = parsed_sqs_msgs[-1]

        sm.process_sessions_from_id(
            next_id_to_process=next_id_to_process,
            start_date="2019-01-01",
            use_historical=use_historical,
        )

        # messages in sqs are not instantly available
        messages = None
        for _ in range(15):
            messages = sqs_q.receive_messages()
            if messages:
                break

            sleep(1)

        assert messages is not None
        parsed_sqs_msgs2 = sqs_msg_parser(messages[0].body)
        first_current_msg = parsed_sqs_msgs2[0]

        assert first_current_msg["_id"] - last_previous_msg["_id"] == 1

    def test_update_use_historical(self):
        sm = SessionMapping()
        sm.setup()

        # switch to current
        result = sm.update_use_historical(
            count=0,
            use_historical=True,
            most_recent_session_time=datetime.now(tz=timezone.utc)
            - timedelta(minutes=15),
        )
        assert result is False

        result = sm.update_use_historical(
            count=10,
            use_historical=True,
            most_recent_session_time=datetime.now(tz=timezone.utc)
            - timedelta(minutes=15),
        )
        assert result is False

        # switch to historical
        # TODO: possible bug
        result = sm.update_use_historical(
            count=10,
            use_historical=True,
            most_recent_session_time=datetime.now(tz=timezone.utc)
            - timedelta(minutes=61),
        )
        assert result is None

        result = sm.update_use_historical(
            count=10,
            use_historical=False,
            most_recent_session_time=datetime.now(tz=timezone.utc)
            - timedelta(minutes=1381),
        )
        assert result is True

        # TODO: possible bug true
        result = sm.update_use_historical(
            count=10,
            use_historical=False,
            most_recent_session_time=datetime.now(tz=timezone.utc)
            - timedelta(minutes=60),
        )
        assert result is None
