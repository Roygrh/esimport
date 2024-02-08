import logging
from datetime import datetime
from datetime import timezone
from os import environ

from esimport_retention_core import gen_previous_month_indices_name
from esimport_retention_core import get_awsauth
from esimport_retention_core import get_signed_es
from esimport_retention_core import is_snapshot_ok
from esimport_retention_core import parse_es_urls

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


def handler():
    try:
        for region, host in parse_es_urls(ES_URLS):
            awsauth = get_awsauth(region, temporary_creds=True)
            es = get_signed_es(host=host, awsauth=awsauth)
            for index_name in gen_previous_month_indices_name(
                ES_RETENTION_INDICES_PREFIXES, datetime.now(tz=timezone.utc)
            ):
                result = is_snapshot_ok(
                    es, repo_name=SNAPSHOT_REPO_NAME, index_name=index_name
                )
                if result is not True:
                    raise Exception(f"Snapshot for {index_name} is BROKEN!")
                logger.info(f"Snapshot for {index_name} is OK.")

    except Exception as err:
        logger.exception(err)
        raise err


def lambda_handler(event, context):
    handler()
