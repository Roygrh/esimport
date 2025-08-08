import os
from datetime import datetime, timezone, timedelta
import boto3
import pytest
from moto import mock_aws

from esimport.syncers.devices.syncer import DeviceSyncer

TABLE_NAME = "client-tracking-data"
REGION = "us-east-1"

@pytest.fixture(autouse=True)
def _env():
    os.environ["AWS_REGION"] = REGION
    os.environ["DYNAMODB_TABLE_NAME"] = TABLE_NAME
    os.environ["DDB_QUERY_LIMIT"] = "1000"
    yield
    os.environ.pop("AWS_REGION", None)
    os.environ.pop("DYNAMODB_TABLE_NAME", None)
    os.environ.pop("DDB_QUERY_LIMIT", None)

@mock_aws
def test_device_syncer_reads_from_ddb_and_emits_records(monkeypatch):
    # Arrange: DDB with items in range
    ddb = boto3.client("dynamodb", region_name=REGION)
    ddb.create_table(
        TableName=TABLE_NAME,
        AttributeDefinitions=[{"AttributeName": "ID", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "ID", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )

    now = datetime.now(timezone.utc)
    in_range = (now - timedelta(minutes=1)).isoformat()

    ddb.put_item(
        TableName=TABLE_NAME,
        Item={
            "ID": {"S": "k1"},
            "DateUTC": {"S": in_range},
            "IP": {"S": "10.0.0.1"},
            "MAC": {"S": "aa:bb:cc:dd:ee:ff"},
            "UserAgentRaw": {"S": "UA"},
            "Device": {"S": "Phone"},
            "Platform": {"S": "iOS"},
            "Browser": {"S": "Safari"},
            "Username": {"S": "alice"},
            "MemberID": {"S": "123"},
            "MemberNumber": {"S": "M001"},
            "ServiceArea": {"S": "SA1"},
            "ZoneType": {"S": "public"},
        },
    )

    # Capture the Records that would be "published"
    captured = []
    def fake_add_record(self, record):
        captured.append(record)

    monkeypatch.setattr(DeviceSyncer, "add_record", fake_add_record, raising=True)

    # Act
    syncer = DeviceSyncer()
    syncer.setup()  # if you do nothing, nothing happens
    syncer.sync(start_date=now - timedelta(minutes=10))

    # Assert
    assert len(captured) == 1
    rec = captured[0]
    assert rec.id is None  # ES will generate _id
    assert rec.body["IP"] == "10.0.0.1"
    assert "DateUTC" in rec.body
    # index derived from the date (format depends on your implementation)
    assert isinstance(rec.index, str) and len(rec.index) > 0
