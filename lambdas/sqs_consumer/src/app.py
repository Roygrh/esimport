import os
import json
import logging
from base64 import b64decode
from bz2 import decompress
import sentry_sdk
import boto3
from elasticsearch import Elasticsearch, helpers, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

FORMAT = "%(asctime)-15s %(filename)s %(lineno)d %(message)s"
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
SENTRY_DSN = os.environ.get("SENTRY_DSN")
sentry_sdk.init(SENTRY_DSN)

try:
    _log_level = os.environ.get("LOG_LEVEL")
    LOG_LEVEL = logging.getLevelName(_log_level)
    log.setLevel(LOG_LEVEL)
except ValueError as _err:
    log.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        index(event)
    except Exception as err:
        log.exception(err)
        sentry_sdk.capture_exception(err)
        raise err


def index(event):
    records_json_str = event["Records"][0]["body"]

    try:
        records = json.loads(records_json_str)
    except json.decoder.JSONDecodeError:
        log.info(
            "Failed to decode the records payload. Probably compressed, trying to decompress..."
        )
        records_json_str = b64decode(records_json_str)
        records_json_str = decompress(records_json_str).decode("utf-8")
        records = json.loads(records_json_str)
        log.info("Records payload successfully decomprssed.")

    number_of_records = len(records)
    log.info("About to index %d" % (number_of_records,))

    try:
        es = get_es_instance()
        helpers.bulk(es, records, request_timeout=30)
    except helpers.BulkIndexError as bie:
        number_of_errors = len(bie.errors)
        conflict_errors = 0

        for error in bie.errors:
            if is_version_conflict_error(error):
                conflict_errors += 1

        log.warning(
            "Got %.2d errors, %.2d of which are IGNORED conflict errors."
            % (number_of_errors, conflict_errors)
        )

        if number_of_errors > conflict_errors:
            raise

    success_message = "Successfully indexed %.2d document(s)" % (number_of_records,)
    log.info(success_message)

    return {"message": success_message}


def is_version_conflict_error(error):
    for op_type, values in error.items():
        status = values.get("status")
        return status == 409
    return False


def get_es_instance():
    session = boto3.Session()
    credentials = session.get_credentials()

    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        session.region_name,
        "es",
        session_token=credentials.token,
    )

    return Elasticsearch(
        os.environ["ES_URL"],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
