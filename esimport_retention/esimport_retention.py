import logging
from datetime import datetime
from os import environ
from typing import List

# botocore install dateutil as dependency
from dateutil import relativedelta
from elasticsearch import Elasticsearch
from sentry_sdk import capture_exception
import sentry_sdk

FORMAT = "%(asctime)-15s %(filename)s %(lineno)d %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)

# in months
MAX_AGE = environ.get("ES_RETENTION_POLICY_MONTHS")
ES_URLS = environ.get("ES_URLS")
SENTRY_DSN = environ.get("SENTRY_DSN")
ES_RETENTION_INDICES_PREFIXES = environ.get("ES_RETENTION_INDICES_PREFIXES")

try:
    _log_level = environ.get("LOG_LEVEL")
    LOG_LEVEL = logging.getLevelName(_log_level)
    logger.setLevel(LOG_LEVEL)
except ValueError as _err:
    logger.setLevel(logging.INFO)


sentry_sdk.init(SENTRY_DSN)


def parse_es_urls(es_urls: str) -> List[str]:
    return [x.strip() for x in es_urls.split(",")]


def filter_old_indices(index_name: str, retention_month: datetime) -> bool:
    index_prefix, index_date = index_name.split("-", 1)
    index_date = datetime.strptime(index_date, "%Y-%m")
    if index_date <= retention_month:
        return True
    return False


def get_last_retention_month(now: datetime, age: int) -> datetime:
    retention_date = now - relativedelta.relativedelta(months=age)
    return retention_date.replace(day=1)


def get_indices(
    es: Elasticsearch, index_wildcard: str, max_age: int, start_date: datetime
) -> List[str]:
    indices_names = es.indices.get_settings(index=index_wildcard).keys()
    old_indices_iter = filter(
        lambda x: filter_old_indices(x, get_last_retention_month(start_date, max_age)),
        indices_names,
    )
    old_indices = [x for x in old_indices_iter]

    return old_indices


def gen_indices_wildcard(indices_prefixes_str: str) -> List[str]:
    return [f"{x.strip()}-*" for x in indices_prefixes_str.split(",")]


def remove_old_indices(es: Elasticsearch, old_indices: List[str]):
    for index_name in old_indices:
        es.indices.delete(index=index_name)


def __handler():
    try:
        es_urls = parse_es_urls(ES_URLS)
        max_age = int(MAX_AGE)
        for cluster_url in es_urls:
            es = Elasticsearch([cluster_url])
            for index_wildcard in gen_indices_wildcard(ES_RETENTION_INDICES_PREFIXES):
                old_indices = get_indices(es, index_wildcard, max_age, datetime.now())
                remove_old_indices(es, old_indices)
    except Exception as err:
        logger.exception(err)
        capture_exception(err)
        raise err


def lambda_handler(event, context):
    __handler()
