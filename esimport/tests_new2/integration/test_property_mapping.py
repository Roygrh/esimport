import json

from esimport.cache import CacheClient
from esimport.mappings.property import PropertyMapping
from esimport.tests_new2.base_fixutres import *
from esimport.tests_new2.test_helpers import fetch_sqs_messages
from esimport.tests_new2.test_helpers import sqs_msg_parser
from esimport.utils import esimport_json_dumps


class TestPropertyMapping:
    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_properties_from_id(self, latest_ids_table, sqs_q):
        pm = PropertyMapping()
        pm.setup()
        pm.default_query_limit = 4

        pm.process_properties_from_id(next_id_to_process=0)

        # messages in sqs are not instantly available
        messages = fetch_sqs_messages(sqs_q)
        assert len(messages[0].body.split("\n")) == 4

    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_property_sequence_maintained(self, latest_ids_table, sqs_q):
        pm = PropertyMapping()
        pm.setup()
        pm.default_query_limit = 4

        count, next_id_to_process = pm.process_properties_from_id(next_id_to_process=0)

        # messages in sqs are not instantly available
        messages = fetch_sqs_messages(sqs_q)
        parsed_sqs_msgs = sqs_msg_parser(messages[0].body)
        last_previous_msg = parsed_sqs_msgs[-1]

        pm.process_properties_from_id(next_id_to_process=next_id_to_process)

        # messages in sqs are not instantly available
        messages = fetch_sqs_messages(sqs_q)
        parsed_sqs_msgs2 = sqs_msg_parser(messages[0].body)
        first_current_msg = parsed_sqs_msgs2[0]

        assert first_current_msg["_id"] - last_previous_msg["_id"] == 1

    @pytest.mark.usefixtures("empty_q", "empty_table", "clear_redis")
    def test_get_property_by_org_number(self):
        cc = CacheClient()

        assert cc.exists("GL-236-20") is False

        pm = PropertyMapping()
        pm.setup()

        # "GL-236-20" (org category 3) - hardcoded value created by scripts that create tables
        result_db = pm.get_property_by_org_number("GL-236-20")
        assert result_db is not None
        assert cc.exists("GL-236-20") is True

        result_cache = pm.get_property_by_org_number("GL-236-20")

        # cache is storing json object, db return python dict with python objects like datetime
        # converting result from db to compare it with result from cache
        result_db = json.loads(esimport_json_dumps(result_db))
        assert result_db == result_cache

        empty_result = pm.get_property_by_org_number("not-exists")
        assert empty_result is None
