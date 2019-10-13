from datetime import timedelta

from esimport_datadog import EsimportDatadogLogger
from esimport_datadog import LOOK_BACK_FOR_X_MINUTES
from esimport_datadog import doc_types
from tests.base_fixtures import *


time_params = [(1, 1), (15, 15)]


def gen_test_params():
    for doc_type, doc_params in doc_types.items():
        for time_param in time_params:
            yield doc_type, doc_params[1], time_param[0], time_param[1]


class TestEsimportDatadogLogger:
    @pytest.mark.parametrize(
        "doc_type, date_field_name, minutes_behind, result_teimdelta", gen_test_params()
    )
    def test_extract_doc_datetime(
        self, doc_type, date_field_name, minutes_behind, result_teimdelta
    ):
        now = datetime.now(tz=timezone.utc)

        # fmt: off
        result = {
            "hits": {
                "total": 1,
                "hits": [
                    {"_source": {date_field_name: (now + timedelta(minutes=-minutes_behind)).isoformat()}}
                ],
            }
        }
        # fmt: on

        result_timedelta = EsimportDatadogLogger.extract_doc_datetime(
            result, date_field_name, now
        )
        assert (
            result_timedelta.total_seconds()
            == timedelta(minutes=result_teimdelta).total_seconds()
        )

    def test_extract_doc_datetime_empty_result(self):
        now = datetime.now(tz=timezone.utc)
        # fmt: off
        result = {
            "hits": {
                "total": 0,
                "hits": [
                    {"_source": {}}
                ],
            }
        }
        # fmt: on
        result_timedelta = EsimportDatadogLogger.extract_doc_datetime(
            result, "Created", now
        )
        assert (
            result_timedelta.total_seconds()
            == timedelta(minutes=LOOK_BACK_FOR_X_MINUTES).total_seconds()
        )
