import pytest
from elasticsearch import Elasticsearch

from esimport import settings


@pytest.fixture()
def empty_es_aliases(es):
    # ignoring 404 because before test start may not exists
    es.indices.delete_alias(index="_all", name="_all", ignore=[404])

    yield

    es.indices.delete_alias(index="_all", name="_all", ignore=[404])


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
