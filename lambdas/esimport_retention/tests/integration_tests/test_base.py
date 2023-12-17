from datetime import datetime
from datetime import timezone
from os import environ
from time import sleep

import elasticsearch.exceptions
import pytest
from dateutil import relativedelta
from elasticsearch import Elasticsearch

import esimport_retention
import esimport_snapshot_creation
import esimport_snapshot_verifier
from esimport_retention_core import delete_snapshot
from esimport_retention_core import gen_previous_month_indices_name
from esimport_retention_core import get_awsauth
from esimport_retention_core import get_last_retention_month
from esimport_retention_core import get_repo_definition
from esimport_retention_core import get_signed_es
from esimport_retention_core import get_snapshot_body
from esimport_retention_core import is_snapshot_ok
from esimport_retention_core import parse_es_urls
from esimport_retention_core import put_test_document
from esimport_retention_core import register_snapshot_repo
from esimport_retention_core import take_snapshot

ES_URLS = environ.get("ES_URLS")
SNAPSHOT_REPO_NAME = environ.get("SNAPSHOT_REPO_NAME")
ES_RETENTION_INDICES_PREFIXES = environ.get("ES_RETENTION_INDICES_PREFIXES")
ES_RETENTION_POLICY_MONTHS = int(environ.get("ES_RETENTION_POLICY_MONTHS"))
S3_BUCKET_NAME = environ.get("S3_BUCKET_NAME")
S3_BUCKET_REGION = environ.get("S3_BUCKET_REGION")
S3_ACCESS_ROLE_ARN = environ.get("S3_ACCESS_ROLE_ARN")


@pytest.fixture(scope="module")
def es():
    (region, host) = parse_es_urls(ES_URLS)[0]
    aws_auht = get_awsauth(region)
    es = get_signed_es(host, aws_auht)
    return es


@pytest.fixture(scope="module")
def register_repository(es):
    repo_definition = get_repo_definition(
        S3_BUCKET_NAME, S3_BUCKET_REGION, S3_ACCESS_ROLE_ARN
    )
    register_snapshot_repo(es, SNAPSHOT_REPO_NAME, repo_definition)


@pytest.fixture()
def clean_indices(es: Elasticsearch):
    all_indices = es.indices.get_settings(index="*").keys()
    for index_name in all_indices:
        es.indices.delete(index=index_name)
    yield
    all_indices = es.indices.get_settings(index="*").keys()
    for index_name in all_indices:
        es.indices.delete(index=index_name)


@pytest.fixture()
def clean_snapshots(es: Elasticsearch):
    result = es.snapshot.get(repository=SNAPSHOT_REPO_NAME, snapshot=["_all"])
    all_snapshots = map(lambda x: x["snapshot"], result["snapshots"])
    for snapshot_name in all_snapshots:
        es.snapshot.delete(repository=SNAPSHOT_REPO_NAME, snapshot=snapshot_name)
    yield
    result = es.snapshot.get(repository=SNAPSHOT_REPO_NAME, snapshot=["_all"])
    all_snapshots = map(lambda x: x["snapshot"], result["snapshots"])
    for snapshot_name in all_snapshots:
        es.snapshot.delete(repository=SNAPSHOT_REPO_NAME, snapshot=snapshot_name)


class TestSnapshotCreation:
    @pytest.mark.usefixtures("register_repository", "clean_snapshots")
    def test_take_snapshot_verify_snapshot_delete_snapshot(self, es):
        index_name = "int_index_name"
        put_test_document(es, index_name)
        snapshot_body = get_snapshot_body(index_name)
        take_snapshot(
            es,
            repo_name=SNAPSHOT_REPO_NAME,
            index_name=index_name,
            snapshot_body=snapshot_body,
        )

        # to allow snapshot be created
        sleep(3)
        result = is_snapshot_ok(es, repo_name=SNAPSHOT_REPO_NAME, index_name=index_name)
        assert result is True

        delete_snapshot(es, repo_name=SNAPSHOT_REPO_NAME, index_name=index_name)

        # to allow snapshot be deleted
        sleep(3)
        result = es.snapshot.get(repository=SNAPSHOT_REPO_NAME, snapshot=["_all"])
        all_snapshots = list(map(lambda x: x["snapshot"], result["snapshots"]))
        assert all_snapshots == []

    @pytest.mark.usefixtures("register_repository", "clean_snapshots")
    def test_is_snapshot_ok(self, es):
        index_name = "int_index_name"
        put_test_document(es, index_name)
        snapshot_body = get_snapshot_body(index_name)
        take_snapshot(
            es,
            repo_name=SNAPSHOT_REPO_NAME,
            index_name=index_name,
            snapshot_body=snapshot_body,
        )

        # quick check, should return False
        result = is_snapshot_ok(es, repo_name=SNAPSHOT_REPO_NAME, index_name=index_name)
        assert result is False

        # not existed index, should return False
        result = is_snapshot_ok(
            es, repo_name=SNAPSHOT_REPO_NAME, index_name="not_existed_index"
        )
        assert result is False


class TestLambdaHandlers:
    @pytest.mark.usefixtures("register_repository", "clean_snapshots", "clean_indices")
    def test_esimport_snapshot_creation(self, es):
        # --- indices prefixes not configured
        esimport_snapshot_creation.ES_RETENTION_INDICES_PREFIXES = ""
        try:
            esimport_snapshot_creation.handler()
            esimport_snapshot_creation.ES_RETENTION_INDICES_PREFIXES = (
                ES_RETENTION_INDICES_PREFIXES
            )
        except Exception as err:
            pytest.fail(f"Should not raise exception {err}")

        # --- indices does not exists
        with pytest.raises(elasticsearch.exceptions.NotFoundError):
            esimport_snapshot_creation.handler()

        # --- indexes exists

        current_date = datetime.now(tz=timezone.utc)
        for index_name in gen_previous_month_indices_name(
            ES_RETENTION_INDICES_PREFIXES, current_date
        ):
            put_test_document(es, index_name=index_name)

        # to allow indexes be created
        sleep(3)

        try:
            esimport_snapshot_creation.handler()
        except Exception as err:
            pytest.fail(f"Should not raise exception {err}")

        # # to allow snapshot be created
        sleep(3)
        result = es.snapshot.get(repository=SNAPSHOT_REPO_NAME, snapshot=["_all"])[
            "snapshots"
        ]

        result = list(map(lambda x: (x["snapshot"], x["state"]), result))
        previous_month = current_date - relativedelta.relativedelta(months=1)
        date_suffix = f"{previous_month.year}-{previous_month.month:02d}"
        expected = [
            (f"snapshot_a-a-a-{date_suffix}", "SUCCESS"),
            (f"snapshot_b-b-b-{date_suffix}", "SUCCESS"),
            (f"snapshot_c-c-c-{date_suffix}", "SUCCESS"),
        ]
        assert result == expected

    @pytest.mark.usefixtures("register_repository", "clean_snapshots", "clean_indices")
    def test_esimport_snapshot_verifier(self, es):
        # --- indices prefixes not configured
        esimport_snapshot_verifier.ES_RETENTION_INDICES_PREFIXES = ""
        try:
            esimport_snapshot_verifier.handler()
            esimport_snapshot_verifier.ES_RETENTION_INDICES_PREFIXES = (
                ES_RETENTION_INDICES_PREFIXES
            )
        except Exception as err:
            pytest.fail(f"Should not raise exception {err}")

        # --- snapshots does not exists
        with pytest.raises(Exception):
            esimport_snapshot_verifier.handler()

        # --- snapshots exists
        for index_name in gen_previous_month_indices_name(
            ES_RETENTION_INDICES_PREFIXES, datetime.now(tz=timezone.utc)
        ):
            put_test_document(es, index_name=index_name)

        # to allow indexes be created
        sleep(3)
        esimport_snapshot_creation.handler()
        # to allow snapshot be created
        sleep(3)

        try:
            esimport_snapshot_verifier.handler()
        except Exception as err:
            pytest.fail(f"Should not raise exception {err}")

    @pytest.mark.usefixtures("register_repository", "clean_snapshots", "clean_indices")
    def test_esimport_retention(self, es):
        # --- indices prefixes not configured
        esimport_snapshot_creation.ES_RETENTION_INDICES_PREFIXES = ""
        try:
            esimport_retention.handler()
            esimport_retention.ES_RETENTION_INDICES_PREFIXES = (
                ES_RETENTION_INDICES_PREFIXES
            )
        except Exception as err:
            pytest.fail(f"Should not raise exception {err}")

        # --- snapshots does not exists or status of snapshots is not SUCCESS
        last_month_to_keep = get_last_retention_month(
            datetime.now(tz=timezone.utc), ES_RETENTION_POLICY_MONTHS
        )

        generated_indexes = []
        for index_name in gen_previous_month_indices_name(
            ES_RETENTION_INDICES_PREFIXES, last_month_to_keep
        ):
            generated_indexes.append(index_name)
            put_test_document(es, index_name=index_name)

        with pytest.raises(Exception):
            esimport_retention.handler()

        # --- snapshots exists
        for index_name in gen_previous_month_indices_name(
            ES_RETENTION_INDICES_PREFIXES, last_month_to_keep
        ):
            snapshot_body = get_snapshot_body(index_name)
            take_snapshot(
                es,
                repo_name=SNAPSHOT_REPO_NAME,
                index_name=index_name,
                snapshot_body=snapshot_body,
            )

        # to allow snapshot be created
        sleep(3)
        result = es.indices.get_settings(index=["_all"]).keys()

        # AWS may create index '.kibana', using sets logic
        assert set(generated_indexes).issubset(set(result)) is True

        esimport_retention.handler()
        result = es.indices.get_settings(index=["_all"]).keys()
        assert set(generated_indexes).isdisjoint(set(result)) is True
