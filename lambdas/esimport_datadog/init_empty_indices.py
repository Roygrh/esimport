import argparse
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from esimport_datadog import EsimportDatadogLogger
from esimport_datadog import doc_types
from tests.integration.base_integration_test import __create_empty_indices

# set ES_URL and LOOK_BACK_FOR_X_MINUTES env variable, it required by EsimportDatadogLogger class

parser = argparse.ArgumentParser(
    description="Tool that create indices with or without documents to manually test esimport_datadog",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--with-docs",
    action="store_true",
    help="will create indices with document 5 minutes behind",
)


parsed_args = parser.parse_args()


edl = EsimportDatadogLogger()
try:
    __create_empty_indices(edl.es)
except Exception as err:
    if err.error == "index_already_exists_exception":
        pass
    else:
        raise err

if parsed_args.with_docs is True:
    expected_minutes_behind = 5

    doc_datetime = datetime.now(tz=timezone.utc) - timedelta(
        minutes=expected_minutes_behind
    )
    for doc_type, params in doc_types.items():
        index_name, date_field, metric_name = params
        doc_body = {"ID": 1, date_field: doc_datetime.isoformat()}
        edl.es.index(index=index_name, doc_type=doc_type, body=doc_body)
