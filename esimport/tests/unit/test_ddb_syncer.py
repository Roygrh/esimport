import os
import boto3
import pytest

from moto import mock_dynamodb2

from esimport.syncers.devices.ddb_syncer import DeviceDdbSyncer, TABLE_NAME
from esimport.syncers.devices._schema import Device

@mock_dynamodb2
def test_fetch_single_item(monkeypatch):
    # 1) Prepare mock table
    region = "us-east-1"
    os.environ["DYNAMODB_TABLE_NAME"] = "client-tracking-data"
    # Create table with only HASH key "ID"
    ddb = boto3.resource("dynamodb", region_name=region)
    ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "ID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "ID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )
    table = ddb.Table(TABLE_NAME)

    # 2) Insert an item within the range
    item = {
        "ID": "abc123",
        "DateUTC": "2025-07-01T12:00:00Z",
        "IP": "1.2.3.4",
        "MAC": "AA:BB:CC:DD",
        "Device": "Phone"
    }
    table.put_item(Item=item)

    # 3) Run fetch and check
    syncer = DeviceDdbSyncer()
    results = list(syncer.fetch("2025-07-01T00:00:00Z", "2025-07-02T00:00:00Z", limit=10))

    assert len(results) == 1
    device: Device = results[0]
    assert isinstance(device, Device)
    assert device.MAC == "AA:BB:CC:DD"
    assert device.Date == "2025-07-01T12:00:00Z"
    assert device.id is None  # should be None to let ES generate the _id

@mock_dynamodb2
def test_fetch_pagination(monkeypatch):
    # Set up environment
    os.environ["DYNAMODB_TABLE_NAME"] = "client-tracking-data"
    region = "us-east-1"
    ddb = boto3.resource("dynamodb", region_name=region)
    table = ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "ID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "ID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )

    # Insert multiple items (> limit)
    for i in range(15):
        table.put_item(Item={
            "ID": f"id-{i}",
            "DateUTC": "2025-07-01T12:00:00Z",
            "IP": f"1.2.3.{i}",
            "MAC": f"AA:BB:CC:{i:02X}"
        })

    # Monkeypatch to force limit=5
    syncer = DeviceDdbSyncer()
    results = list(syncer.fetch("2025-07-01T00:00:00Z", "2025-07-02T00:00:00Z", limit=5))
    # Should return 15 items in total, despite the internal limit per page
    assert len(results) == 15

