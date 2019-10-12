import logging
from datetime import datetime
from typing import List

import boto3
from dateutil import relativedelta
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
from requests_aws4auth import AWS4Auth
from urllib3.util import parse_url

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_awsauth(region: str, temporary_creds: bool = False) -> AWS4Auth:
    credentials = boto3.Session().get_credentials()
    session_creds = None
    if temporary_creds is True:
        session_creds = credentials.token
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        "es",
        session_token=session_creds,
    )
    return awsauth


def get_signed_es(host: str, awsauth: AWS4Auth) -> Elasticsearch:
    es = Elasticsearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    return es


def get_repo_definition(s3_bucket_name: str, region: str, role_arn: str) -> dict:
    return {
        "type": "s3",
        "settings": {"bucket": s3_bucket_name, "region": region, "role_arn": role_arn},
    }


def get_repo_info(es: Elasticsearch, repo_name: str):
    result = es.snapshot.get_repository(repository=[repo_name])
    return result


def get_snapshot_body(index_name: str) -> dict:
    return {
        "indices": index_name,
        "ignore_unavailable": False,
        "include_global_state": False,
    }


def parse_es_url(url: str) -> tuple:
    region = url.split(".")[-4]
    return region, parse_url(url).host


def parse_es_urls(es_urls: str) -> List[tuple]:
    es_urls = es_urls.strip(",")
    return [parse_es_url(x.strip()) for x in es_urls.split(",")]


def take_snapshot(
    es: Elasticsearch, repo_name: str, index_name: str, snapshot_body: dict
):
    snapshot_name = f"snapshot_{index_name}"
    result = es.snapshot.create(
        repository=repo_name, snapshot=snapshot_name, body=snapshot_body
    )
    logger.info(result)
    return result


def delete_snapshot(es: Elasticsearch, repo_name: str, index_name: str):
    snapshot_name = f"snapshot_{index_name}"
    result = es.snapshot.delete(repository=repo_name, snapshot=snapshot_name)
    logger.info(result)
    return result


def is_snapshot_ok(es: Elasticsearch, repo_name: str, index_name: str):
    try:
        snapshot_name = f"snapshot_{index_name}"
        result = es.snapshot.get(repository=repo_name, snapshot=[snapshot_name])

        logger.info(result)
        if result["snapshots"][0]["state"] == "SUCCESS":
            return True

        return False

    except Exception as err:
        logger.exception(err)
        return False


def get_previous_month_str(start_date: datetime):
    previous_month = start_date - relativedelta.relativedelta(months=1)
    return previous_month.strftime("%Y-%m")


def get_old_indices(
    es: Elasticsearch, index_wildcard: str, max_age: int, start_date: datetime
) -> List[str]:
    indices_names = es.indices.get_settings(index=index_wildcard).keys()

    old_indices_iter = filter(
        lambda x: filter_old_indices(x, get_last_retention_month(start_date, max_age)),
        indices_names,
    )
    old_indices = [x for x in old_indices_iter]

    return old_indices


def filter_old_indices(index_name: str, retention_month: datetime) -> bool:
    index_name_parts = index_name.split("-")
    # index_prefix = '-'.join(index_name_parts[:-2])
    index_date = datetime.strptime("-".join(index_name_parts[-2:]), "%Y-%m")
    if index_date <= retention_month:
        return True
    return False


def get_last_retention_month(now: datetime, age: int) -> datetime:
    retention_date = now - relativedelta.relativedelta(months=age)
    return retention_date.replace(day=1)


def gen_indices_wildcard(indices_prefixes_str: str) -> List[str]:
    if len(indices_prefixes_str.strip()) == 0:
        return []
    return [f"{x.strip()}-*" for x in indices_prefixes_str.split(",")]


def gen_previous_month_indices_name(indices_prefixes_str: str, cur_date: datetime):
    if len(indices_prefixes_str.strip()) == 0:
        return []
    date_str = get_previous_month_str(cur_date)
    return [f"{x.strip()}-{date_str}" for x in indices_prefixes_str.split(",")]


def register_snapshot_repo(es: Elasticsearch, repo_name: str, repo_definition: dict):
    result = es.snapshot.create_repository(repository=repo_name, body=repo_definition)
    print(result)


def put_test_document(es, index_name):
    # fmt: off
    sample_docs = [
        {"_index": index_name, "_type": "a", "_id": 1, "doc_as_upsert": True, "doc": {"ID": 1}},
        {"_index": index_name, "_type": "a", "_id": 2, "doc_as_upsert": True, "doc": {"ID": 2}},
    ]
    # fmt: on
    helpers.bulk(es, sample_docs)
