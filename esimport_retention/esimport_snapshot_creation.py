import logging
from datetime import datetime
from os import environ

import sentry_sdk
from sentry_sdk import capture_exception

from esimport_retention_core import gen_previous_month_indices_name
from esimport_retention_core import get_awsauth
from esimport_retention_core import get_signed_es
from esimport_retention_core import get_snapshot_body
from esimport_retention_core import parse_es_urls
from esimport_retention_core import take_snapshot

FORMAT = "%(asctime)-15s %(filename)s %(lineno)d %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)


try:
    _log_level = environ.get("LOG_LEVEL")
    LOG_LEVEL = logging.getLevelName(_log_level)
    logger.setLevel(LOG_LEVEL)
except ValueError as _err:
    logger.setLevel(logging.INFO)


SNAPSHOT_REPO_NAME = environ.get("SNAPSHOT_REPO_NAME")
ES_URLS = environ.get("ES_URLS")
ES_RETENTION_INDICES_PREFIXES = environ.get("ES_RETENTION_INDICES_PREFIXES")
SENTRY_DSN = environ.get("SENTRY_DSN")

sentry_sdk.init(SENTRY_DSN)


def handler():
    try:
        for (region, host) in parse_es_urls(ES_URLS):
            awsauth = get_awsauth(region, temporary_creds=True)
            es = get_signed_es(host=host, awsauth=awsauth)
            for index_name in gen_previous_month_indices_name(
                ES_RETENTION_INDICES_PREFIXES, datetime.utcnow()
            ):
                logger.info(index_name)
                snapshot_body = get_snapshot_body(index_name)
                take_snapshot(
                    es,
                    repo_name=SNAPSHOT_REPO_NAME,
                    index_name=index_name,
                    snapshot_body=snapshot_body,
                )
    except Exception as err:
        # if snapshot with same name already exists skipping error
        if "snapshot with the same name already exists" in repr(err):
            return

        logger.exception(err)
        capture_exception(err)
        raise err


def lambda_handler(event, context):
    handler()
