from esimport.mappings.conference import ConferenceMapping
from esimport.tests_new2.base_fixutres import *
from esimport.tests_new2.test_helpers import fetch_sqs_messages
from esimport.tests_new2.test_helpers import sqs_msg_parser


class TestConferenceMapping:
    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_conferences_from_id(self, latest_ids_table, sqs_q):
        cm = ConferenceMapping()
        cm.setup()
        cm.default_query_limit = 4

        cm.process_conferences_from_id(next_id_to_process=0, start_date="2019-01-01")

        # messages in sqs are not instantly available
        messages = fetch_sqs_messages(sqs_q)
        assert len(messages[0].body.split("\n")) == 4

    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_conferences_sequence_maintained(self, latest_ids_table, sqs_q):
        cm = ConferenceMapping()
        cm.setup()
        cm.default_query_limit = 4

        count, next_id_to_process = cm.process_conferences_from_id(
            next_id_to_process=0, start_date="2019-01-01"
        )

        # messages in sqs are not instantly available
        messages = fetch_sqs_messages(sqs_q)
        parsed_sqs_msgs = sqs_msg_parser(messages[0].body)
        last_previous_msg = parsed_sqs_msgs[-1]

        # consequent call
        cm.process_conferences_from_id(
            next_id_to_process=next_id_to_process, start_date="2019-01-01"
        )

        messages = fetch_sqs_messages(sqs_q)
        parsed_sqs_msgs2 = sqs_msg_parser(messages[0].body)
        first_current_msg = parsed_sqs_msgs2[0]

        assert first_current_msg["_id"] - last_previous_msg["_id"] == 1
