import pytest
from elasticsearch import Elasticsearch, helpers
from datetime import datetime
from esimport_retention import get_indices
from esimport_retention import remove_old_indices


@pytest.fixture(scope="module")
def es():
    return Elasticsearch("localhost:9200")


@pytest.fixture()
def sample_data(es: Elasticsearch):
    # fmt: off
    sample_docs = [
        {"_index": "a-2018-01", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-02", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-03", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-04", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-05", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-06", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-07", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-08", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-09", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-10", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-11", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2018-12", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-01", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-02", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-03", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-04", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-05", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-06", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-07", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-08", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-09", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-10", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-11", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": "a-2019-12", "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
    ]
    # fmt: on
    helpers.bulk(es, sample_docs)
    yield
    all_indices = es.indices.get_settings(index="*").keys()
    for index_name in all_indices:
        es.indices.delete(index=index_name)


class TestIndicesRetention:
    @pytest.mark.usefixtures("sample_data")
    def test_get_indices(self, es: Elasticsearch):
        retention_policy = 18
        old_indices = get_indices(es, "a-*", retention_policy, datetime(2019, 12, 15))

        expected = [
            "a-2018-01",
            "a-2018-02",
            "a-2018-03",
            "a-2018-04",
            "a-2018-05",
            "a-2018-06",
        ]
        assert sorted(old_indices) == expected

        retention_policy = 24
        old_indices = get_indices(es, "a-*", retention_policy, datetime(2019, 12, 15))

        expected = []
        assert sorted(old_indices) == expected

        retention_policy = 1
        old_indices = get_indices(es, "a-*", retention_policy, datetime(2018, 2, 15))

        expected = ["a-2018-01"]
        assert sorted(old_indices) == expected

        retention_policy = 1
        old_indices = get_indices(es, "a-*", retention_policy, datetime(2018, 1, 15))

        expected = []
        assert sorted(old_indices) == expected

    @pytest.mark.usefixtures("sample_data")
    def test_remove_old_indices(self, es: Elasticsearch):
        retention_policy = 18
        old_indices = get_indices(es, "a-*", retention_policy, datetime(2019, 12, 15))
        print(old_indices)
        remove_old_indices(es, old_indices)

        remain_indices = es.indices.get_settings(index="a-*").keys()
        expected = [
            "a-2018-07",
            "a-2018-08",
            "a-2018-09",
            "a-2018-10",
            "a-2018-11",
            "a-2018-12",
            "a-2019-01",
            "a-2019-02",
            "a-2019-03",
            "a-2019-04",
            "a-2019-05",
            "a-2019-06",
            "a-2019-07",
            "a-2019-08",
            "a-2019-09",
            "a-2019-10",
            "a-2019-11",
            "a-2019-12",
        ]
        assert sorted(remain_indices) == expected
