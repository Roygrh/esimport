import logging
from time import sleep

import elasticsearch.exceptions
from elasticsearch import helpers

from esimport.mappings.indices_definitions import accounts_template_body
from esimport.mappings.indices_definitions import conference_mapping
from esimport.mappings.indices_definitions import devices_template_body
from esimport.mappings.indices_definitions import elevenos_aliases_config
from esimport.mappings.indices_definitions import property_mapping
from esimport.mappings.indices_definitions import sessions_template_body
from esimport.mappings.init_index import create_elevenos_aliases
from esimport.tests_new.integration.basic_fixtures import *

logger = logging.getLogger(__name__)


default_index_props = {"settings": {"number_of_shards": 9, "number_of_replicas": 1}}


@pytest.fixture()
def indices_templates(es):
    index_templates = {
        "accounts": accounts_template_body,
        "sessions": sessions_template_body,
        "devices": devices_template_body,
    }

    for template_name, body in index_templates.items():
        body.update(default_index_props)
        es.indices.put_template(name=template_name, body=body)

    yield

    for template_name in index_templates.keys():
        es.indices.delete_template(name=template_name)


@pytest.fixture()
def test_indices(es):
    new_indices = {
        "properties": {"doc_type": "property", "body": property_mapping},
        "conferences": {"doc_type": "conference", "body": conference_mapping},
    }

    for index_name, props in new_indices.items():
        try:
            es.indices.create(index=index_name, body=default_index_props)
            es.indices.put_mapping(
                index=index_name, doc_type=props["doc_type"], body=props["body"]
            )
        except elasticsearch.exceptions.RequestError as e:
            if e.error != "index_already_exists_exception":
                raise
            err_msg = str(e)
            logger.warning(f"Failed to create {index_name} index, got {err_msg}")

    yield

    for index_name in new_indices.keys():
        es.indices.delete(index=index_name)


@pytest.fixture()
def elevenos_index(es):
    es.indices.create(index="elevenos", body=default_index_props)
    create_elevenos_aliases(es, logger)

    yield

    es.indices.delete(index="elevenos")


def doc_templates(doctype, index_name):
    return [
        {
            "_index": index_name,
            "_type": doctype,
            "_id": 1,
            "doc_as_upsert": True,
            "doc": {"ID": 1},
        },
        {
            "_index": index_name,
            "_type": doctype,
            "_id": 2,
            "doc_as_upsert": True,
            "doc": {"ID": 2},
        },
    ]


def create_docs_in_elevenos(es, indices_vars):
    for doctype in indices_vars.keys():
        smaple_docs = doc_templates(doctype, "elevenos")
        helpers.bulk(es, smaple_docs)


def create_docs_in_separated_indeces(es, indices_vars):
    for doctype, index_name in indices_vars.items():
        smaple_docs = doc_templates(doctype, index_name)
        helpers.bulk(es, smaple_docs)


class TestQueriesResults:

    test_parameters = [
        (
            create_docs_in_elevenos,
            {"account": "elevenos", "device": "elevenos", "session": "elevenos"},
        ),
        (
            create_docs_in_separated_indeces,
            {
                "account": "accounts-2019-01",
                "device": "devices-2019-01",
                "session": "sessions-2019-01",
            },
        ),
    ]

    @pytest.mark.usefixtures(
        "empty_es_indexes", "indices_templates", "test_indices", "elevenos_index"
    )
    @pytest.mark.parametrize("docs_gen_function, indices_vars", test_parameters)
    def test_queries_match(self, es, docs_gen_function, indices_vars):
        """This test runs X times. X = len(test_parameters). Each time documents will be writen to different indices,
        but will be searched from index alias. It will check that ElasticSearch alias configuration return the same
        results not matter where docs are stored.

        Function `doc_templates()` generate content for documents.
        Dictionary `elevenos_aliases_config` store alias configuration based on doctype.


        :param es:
        :param docs_gen_function:
        :param indices_vars:
        :return:
        """
        docs_gen_function(es, indices_vars)

        # to allow documents be indexed
        sleep(2)

        for doctype, index_name in indices_vars.items():
            expected_docs = doc_templates(doctype, index_name)
            query_index_name = elevenos_aliases_config[doctype]

            result = es.search(
                index=query_index_name, body={"query": {"match_all": {}}}
            )
            assert len(expected_docs) == result["hits"]["total"]

            sorted_expected = sorted(expected_docs, key=lambda x: x["_id"])
            sorted_result = sorted(result["hits"]["hits"], key=lambda x: x["_id"])

            for expected, result in zip(sorted_expected, sorted_result):
                assert expected["doc"] == result["_source"]["doc"]
