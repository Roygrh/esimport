import boto3
import pytest


@pytest.fixture
def sqs_q():
    session = boto3.session.Session()
    return session.resource(
        service_name="sqs",
        aws_access_key_id="aaa",
        aws_secret_access_key="bbb",
        region_name="us-west-2",
        endpoint_url="http://localhost:9324",
    ).Queue("http://localhost:9324/queue/default")


@pytest.fixture()
def empty_q():
    session = boto3.session.Session()
    queue = session.resource(
        service_name="sqs",
        aws_access_key_id="aaa",
        aws_secret_access_key="bbb",
        region_name="us-west-2",
        endpoint_url="http://localhost:9324",
    ).Queue("http://localhost:9324/queue/default")
    queue.purge()
    yield
    queue.purge()


@pytest.fixture
def dynamodb_client():
    session = boto3.session.Session()
    return session.client(
        service_name="dynamodb",
        aws_access_key_id="aaa",
        aws_secret_access_key="bbb",
        region_name="us-west-2",
        endpoint_url="http://localhost:8000",
    )


@pytest.fixture
def latest_ids_table():
    session = boto3.session.Session()
    return session.resource(
        service_name="dynamodb",
        aws_access_key_id="aaa",
        aws_secret_access_key="bbb",
        region_name="us-west-2",
        endpoint_url="http://localhost:8000",
    ).Table("latest_ids")


@pytest.fixture
def empty_table(dynamodb_client):
    dynamodb_client.create_table(
        AttributeDefinitions=[{"AttributeName": "doctype", "AttributeType": "S"}],
        TableName="latest_ids",
        KeySchema=[{"AttributeName": "doctype", "KeyType": "HASH"}],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    yield
    dynamodb_client.delete_table(TableName="latest_ids")
