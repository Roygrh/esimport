from datetime import timedelta
from time import sleep
from unittest import mock

import esimport_datadog
from esimport_datadog import EsimportDatadogLogger
from esimport_datadog import doc_types
from tests import indicides_definition
from tests.base_fixtures import *

time_params = [(1, 1, 1), (15, 0, None)]


def gen_test_params():
    for doc_type, doc_params in doc_types.items():
        for time_param in time_params:
            yield doc_type, doc_params[1], time_param[0], time_param[1], time_param[2]


def __create_empty_indices(es_hndl: Elasticsearch):
    for doc_type, params in doc_types.items():
        index_name = params[0]
        mapping = getattr(indicides_definition, f"{doc_type}_mapping")
        creation_body = {"mappings": {doc_type: mapping}}

        es_hndl.indices.create(index=index_name, body=creation_body)


@pytest.fixture()
def create_empty_indices(local_es: Elasticsearch):
    __create_empty_indices(local_es)


@pytest.fixture()
def test_config_for_look_back_for():
    # Explicitly setting this value,
    #
    # If indices contains documents - ``process()` will return result with minutes_behind == expected_minutes_behind
    # If indices does not contains any documents -  `process()` will return result with
    # minutes_behind == esimport_datadog.LOOK_BACK_FOR_X_MINUTES

    original_value = esimport_datadog.LOOK_BACK_FOR_X_MINUTES
    esimport_datadog.LOOK_BACK_FOR_X_MINUTES = 20
    yield
    esimport_datadog.LOOK_BACK_FOR_X_MINUTES = original_value


class TestIntegrationEsimportDatadogLogger:
    @pytest.mark.parametrize(
        "doc_type, date_field_name, creation_time, total_hits, time_in_doc",
        gen_test_params(),
    )
    @pytest.mark.usefixtures("empty_es_indexes")
    def test_get_last_inserted_doc(
        self,
        local_es: Elasticsearch,
        doc_type: str,
        date_field_name: str,
        creation_time: int,
        total_hits: int,
        time_in_doc: int,
    ):

        created_date = datetime.now(tz=timezone.utc) - timedelta(minutes=creation_time)

        sample_doc = {"ID": 1, date_field_name: created_date}
        local_es.index(index="test-index", doc_type=doc_type, id=1, body=sample_doc)
        sleep(1)
        result = EsimportDatadogLogger.get_last_inserted_doc(
            local_es, "test-index", date_field_name, 10
        )
        assert result["hits"]["total"] == total_hits
        if time_in_doc is not None:
            assert (
                result["hits"]["hits"][0]["_source"][date_field_name]
                == created_date.isoformat()
            )

    @pytest.mark.usefixtures(
        "empty_es_indexes", "create_empty_indices", "test_config_for_look_back_for"
    )
    def test_process_no_latest_doc_found(self, local_es: Elasticsearch):
        edl = EsimportDatadogLogger()
        edl.es = local_es

        with mock.patch(
            "esimport_datadog.EsimportDatadogLogger.put_metric"
        ) as mock_spy:
            edl.process()

        for call_args, doc_type in zip(mock_spy.call_args_list, doc_types.keys()):
            metric_name, minutes_behind, now = call_args[0]

            expected_metric_name = doc_types[doc_type][2]
            assert metric_name == expected_metric_name
            assert minutes_behind == esimport_datadog.LOOK_BACK_FOR_X_MINUTES

    @pytest.mark.usefixtures("empty_es_indexes", "test_config_for_look_back_for")
    def test_process_latest_doc_exists(self, local_es: Elasticsearch):
        expected_minutes_behind = 5

        doc_datetime = datetime.now(tz=timezone.utc) - timedelta(
            minutes=expected_minutes_behind
        )
        for doc_type, params in doc_types.items():
            index_name, date_field, metric_name = params
            mapping = getattr(indicides_definition, f"{doc_type}_mapping")
            creation_body = {"mappings": {doc_type: mapping}}

            local_es.indices.create(index=index_name, body=creation_body)

            doc_body = {"ID": 1, date_field: doc_datetime.isoformat()}
            local_es.index(index=index_name, doc_type=doc_type, body=doc_body)

        # to allow docs be indexed
        sleep(1)

        edl = EsimportDatadogLogger()
        edl.es = local_es

        with mock.patch(
            "esimport_datadog.EsimportDatadogLogger.put_metric"
        ) as mock_spy:
            edl.process()

        for call_args, doc_type in zip(mock_spy.call_args_list, doc_types.keys()):
            metric_name, minutes_behind, doc_date = call_args[0]

            expected_metric_name = doc_types[doc_type][2]
            assert metric_name == expected_metric_name
            assert minutes_behind == expected_minutes_behind
