from esimport.mappings.session import SessionMapping
from time import sleep
from esimport.tests_new2.base_fixutres import *


class TestSessionMapping:
    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_sessions_from_id(self, latest_ids_table, sqs_q):
        sm = SessionMapping()
        sm.setup()

        result = sm.process_sessions_from_id(
            latest_processed_id=0, start_date="1900-01-01", use_historical=True
        )

        # messages in sqs are not instantly available
        messages = None
        for _ in range(15):
            messages = sqs_q.receive_messages()
            if messages:
                break

            sleep(1)

        assert messages is not None
        assert len(messages[0].body.split("\n")) == 8
        # TODO update fixtures and check that order is keept
