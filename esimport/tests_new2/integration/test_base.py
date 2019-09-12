from esimport.mappings.doc import DocumentMapping
import boto3
import pytest
from unittest import mock
from esimport.models import ESRecord
from datetime import timezone
from datetime import datetime
import json
from time import sleep
from io import StringIO

#
# sqs_client = session.client(
#     service_name='sqs',
#     aws_access_key_id='aaa',
#     aws_secret_access_key='bbb',
#     region_name='us-west-2',
#     endpoint_url='http://localhost:9324',
# )
# response = sqs_client.list_queues()
#
# response = dynamodb_client.list_tables()


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


class TestDocumentMapping:
    @pytest.mark.usefixtures("empty_table")
    def test_max_id(self, latest_ids_table):
        dm = DocumentMapping()
        latest_ids_table.put_item(Item={"doctype": "test_doctype", "latest_id": 1})

        class TestModel:
            _type = "test_doctype"

        dm.model = TestModel()
        id = dm.max_id()
        assert id == 1

    def test_add_none(self):
        dm = DocumentMapping()
        with mock.patch(
            "esimport.mappings.doc.DocumentMapping.put_msg_in_q", side_effect=None
        ) as mock_func:
            dm.add(None, None)
            mock_func.assert_called_once()

    @pytest.mark.usefixtures("empty_table")
    def test_add_not_exceeded_batch_size(self, latest_ids_table):
        """Trying to add bulk action, it not exceeding maximum batch size"""

        class TestModel:
            _type = "test_doctype"

        dm = DocumentMapping()
        dm.model = TestModel()
        dm._version_date_fieldname = "test_date_field"

        version_date = datetime.now(tz=timezone.utc).isoformat()
        with mock.patch(
            "esimport.mappings.doc.DocumentMapping.put_msg_in_q"
        ) as mock_func:
            sample_es_record = ESRecord(
                record={"ID": 1, "test_date_field": version_date},
                doc_type="test_type",
                index_prefix="test_index",
                version_date=datetime.now(tz=timezone.utc).isoformat(),
            )
            dm.add(sample_es_record.es(), None)
            mock_func.assert_not_called()
            assert len(dm._items) == 1
            assert dm.current_size == len(
                json.dumps(sample_es_record.es()).encode("utf-8")
            )

    @pytest.mark.usefixtures("empty_q", "empty_table")
    def test_add_exceeded_batch_size(self, sqs_q):
        """Trying to add bulk action, it not exceeding maximum batch size"""

        class TestModel:
            _type = "test_doctype"

        dm = DocumentMapping()
        dm.model = TestModel()
        dm._version_date_fieldname = "test_date_field"

        version_date = datetime.now(tz=timezone.utc).isoformat()

        sample_es_record = ESRecord(
            record={"ID": 1, "test_date_field": version_date},
            doc_type="test_type",
            index_prefix="test_index",
            version_date=version_date,
        )
        for _ in range(3):
            dm.add(sample_es_record.es(), None)

        # changing maximum allowed size of batch, should trigger `put_msg_in_q()` method
        assert len(dm._items) == 3
        dm.max_size = dm.current_size + 1

        dm.add(sample_es_record.es(), None)

        # messages in queue is not available right away
        # staring finite loop to check message availability
        messages = []
        for x in range(15):
            messages = sqs_q.receive_messages()
            if messages:
                break
            sleep(1)

        assert messages != []

        es_actions = messages[0].body.split("\n")
        assert len(es_actions) == 3

        assert len(dm._items) == 1
        assert dm.current_size == len(json.dumps(sample_es_record.es()).encode("utf-8"))
