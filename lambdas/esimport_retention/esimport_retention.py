import logging
from datetime import datetime
from os import environ
from typing import List

import sentry_sdk

# botocore install dateutil as dependency
from elasticsearch import Elasticsearch
from sentry_sdk import capture_exception

from esimport_retention_core import get_awsauth, get_old_indices, gen_indices_wildcard
from esimport_retention_core import get_signed_es
from esimport_retention_core import is_snapshot_ok
from esimport_retention_core import parse_es_urls

FORMAT = "%(asctime)-15s %(filename)s %(lineno)d %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)

# in months
ES_RETENTION_POLICY_MONTHS = environ.get("ES_RETENTION_POLICY_MONTHS")
ES_URLS = environ.get("ES_URLS")
SENTRY_DSN = environ.get("SENTRY_DSN")
ES_RETENTION_INDICES_PREFIXES = environ.get("ES_RETENTION_INDICES_PREFIXES")
SNAPSHOT_REPO_NAME = environ.get("SNAPSHOT_REPO_NAME")

try:
    _log_level = environ.get("LOG_LEVEL")
    LOG_LEVEL = logging.getLevelName(_log_level)
    logger.setLevel(LOG_LEVEL)
except ValueError as _err:
    logger.setLevel(logging.INFO)


sentry_sdk.init(SENTRY_DSN)


def remove_old_indices(es: Elasticsearch, old_indices: List[str], repo_name: str):
    for index_name in old_indices:
        snapshot_ok = is_snapshot_ok(es, repo_name=repo_name, index_name=index_name)
        if snapshot_ok is False:
            raise Exception(
                f"Can not delete index: {index_name}, because snapshot for it does not exists"
            )

        elif snapshot_ok is True:
            logger.info(f"Snapshot for {index_name} exists, deleting index.")
            es.indices.delete(index=index_name)


def handler():
    try:
        max_age = int(ES_RETENTION_POLICY_MONTHS)
        for (region, host) in parse_es_urls(ES_URLS):
            awsauth = get_awsauth(region, temporary_creds=True)
            es = get_signed_es(host=host, awsauth=awsauth)

            for index_wildcard in gen_indices_wildcard(ES_RETENTION_INDICES_PREFIXES):
                old_indices = get_old_indices(
                    es, index_wildcard, max_age, datetime.now()
                )
                remove_old_indices(es, old_indices, repo_name=SNAPSHOT_REPO_NAME)

    except Exception as err:
        logger.exception(err)
        capture_exception(err)
        raise err


def lambda_handler(event, context):
    handler()
