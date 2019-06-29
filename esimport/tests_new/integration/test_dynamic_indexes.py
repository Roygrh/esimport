from elasticsearch import Elasticsearch, helpers

from esimport import settings
from esimport.models import ESRecord
from esimport.models.account import Account
from esimport.models.conference import Conference
from esimport.models.device import Device
from esimport.models.property import Property
from esimport.models.session import Session
from esimport.tests_new.integration.records_fixtures import *


@pytest.fixture(scope="module")
def es():
    return Elasticsearch(f"{settings.ES_HOST}:{settings.ES_PORT}")


@pytest.fixture()
def empty_es_indexes(es):
    indexes_names = es.indices.get_settings(index="*").keys()
    for index_name in indexes_names:
        es.indices.delete(index=index_name)

    yield

    indexes_names = es.indices.get_settings(index="*").keys()
    for index_name in indexes_names:
        es.indices.delete(index=index_name)


@pytest.fixture()
def empty_es_aliases(es):
    # ignoring 404 because before test start may not exists
    es.indices.delete_alias(index="_all", name="_all", ignore=[404])

    yield

    es.indices.delete_alias(index="_all", name="_all")


@pytest.fixture()
def es_templates(es):
    test_settings = {"settings": {"number_of_shards": 9, "number_of_replicas": 1}}
    template_collection = {
        "accounts": {
            "template": "accounts*",
            "settings": test_settings,
            "aliases": {"accounts-current": {}},
        },
        "sessions": {
            "template": "sessions*",
            "settings": test_settings,
            "aliases": {"sessions-current": {}},
        },
        "devices": {
            "template": "devices*",
            "settings": test_settings,
            "aliases": {"devices-current": {}},
        },
    }
    for template_id, body in template_collection.items():
        es.put_template(id=template_id, body=body)


class TestDynamicIndex:
    """Test that dynamic indexes and aliases create correctly

    All indexes for esimport are created automatically. Aliases created by defined templates.
    All `*Mapping` classes are inhereted from `DocumentMapping` class and uses it method add() to put documents in index.
    This method internally uses `elasticsearch.helpers.bulk()` and arguments for this method are created by `ESRecord` class.
    Therefore tests need to check that ESRecord class create correct index name.
    So to tests that indexes are being created correctly, tests in this class create sample `ESRecord` and put it ElasticSearch using
    `elasticsearch.helpers.bulk()`. If `ESRecord()` works correctly, ElasticSearch create expected index and aliases.

    For these tests mapping and other indexes properties are not so important - templates has only basic and alias configuration
    """

    @pytest.mark.usefixtures("empty_es_indexes", "empty_es_aliases", "es_templates")
    def test_dynamic_account_index(self, es, sample_account):
        doc = sample_account["doc"]
        expected_index_name = sample_account["expected_index"]
        account_record = ESRecord(
            doc,
            Account.get_type(),
            Account.get_index(),
            index_date=doc[Account.get_index_date_field()],
        )

        helpers.bulk(es, [account_record.es()])

        indexes_names = es.indices.get_settings(index="*").keys()
        assert sample_account["expected_index"] in indexes_names

        aliases_response = es.indices.get_alias(index=[expected_index_name])
        assert len(aliases_response[expected_index_name]["aliases"]) == 1
        assert (
            sample_account["expected_alias"]
            in aliases_response[expected_index_name]["aliases"].keys()
        )

    @pytest.mark.usefixtures("empty_es_indexes", "empty_es_aliases", "es_templates")
    def test_dynamic_devices_index(self, es, sample_device):
        doc = sample_device["doc"]
        expected_index_name = sample_device["expected_index"]

        device_record = ESRecord(
            doc,
            Device.get_type(),
            Device.get_index(),
            index_date=doc[Device.get_key_date_field()],
        )

        helpers.bulk(es, [device_record.es()])
        indexes_names = es.indices.get_settings(index="*").keys()
        assert sample_device["expected_index"] in indexes_names

        aliases_response = es.indices.get_alias(index=[expected_index_name])
        assert len(aliases_response[expected_index_name]["aliases"]) == 1
        assert (
            sample_device["expected_alias"]
            in aliases_response[expected_index_name]["aliases"].keys()
        )

    @pytest.mark.usefixtures("empty_es_indexes", "empty_es_aliases", "es_templates")
    def test_dynamic_sessions_index(self, es, sample_session):
        doc = sample_session["doc"]
        expected_index_name = sample_session["expected_index"]

        device_record = ESRecord(
            doc,
            Session.get_type(),
            Session.get_index(),
            index_date=doc[Session.get_key_date_field()],
        )

        helpers.bulk(es, [device_record.es()])
        indexes_names = es.indices.get_settings(index="*").keys()
        assert sample_session["expected_index"] in indexes_names

        aliases_response = es.indices.get_alias(index=[expected_index_name])
        assert len(aliases_response[expected_index_name]["aliases"]) == 1
        assert (
            sample_session["expected_alias"]
            in aliases_response[expected_index_name]["aliases"].keys()
        )

    @pytest.mark.usefixtures("empty_es_indexes", "es_templates")
    def test_dynamic_property_index(self, es, sample_property):
        doc = sample_property["doc"]
        property_record = ESRecord(doc, Property.get_type(), Property.get_index())

        helpers.bulk(es, [property_record.es()])
        indexes_names = es.indices.get_settings(index="*").keys()
        assert sample_property["expected_index"] in indexes_names

    @pytest.mark.usefixtures("empty_es_indexes", "es_templates")
    def test_dynamic_conference_index(self, es, sample_conference):
        doc = sample_conference["doc"]
        conference_record = ESRecord(doc, Conference.get_type(), Conference.get_index())

        helpers.bulk(es, [conference_record.es()])
        indexes_names = es.indices.get_settings(index="*").keys()
        assert sample_conference["expected_index"] in indexes_names
