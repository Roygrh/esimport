from esimport.mappings.property import PropertyMapping
from time import sleep
from esimport.tests_new2.base_fixutres import *


class TestPropertyMapping:
    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_process_properties_from_id(self, latest_ids_table, sqs_q):
        pm = PropertyMapping()
        pm.setup()

        result = pm.process_properties_from_id(latest_processed_id=0)

        # messages in sqs are not instantly available
        messages = None
        for _ in range(15):
            messages = sqs_q.receive_messages()
            if messages:
                break

            sleep(1)

        assert messages is not None
        assert len(messages[0].body.split("\n")) == 2
        # TODO update fixtures and check that order is keept

    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_get_property_by_org_number(self):
        # TODO: updated fixtures and then check method properly
        pm = PropertyMapping()
        pm.setup()

        result = pm.get_property_by_org_number("aa-aaa")
        assert result is None
