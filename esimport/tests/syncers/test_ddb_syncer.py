import os
import boto3
import pytest
from moto import mock_dynamodb2

from esimport.syncers.devices.ddb_syncer import DeviceDdbSyncer, TABLE_NAME
from esimport.syncers.devices._schema import Device

@mock_dynamodb2
def test_fetch_single_item(monkeypatch):
    # 1) Preparar tabla mock
    region = "us-east-1"
    os.environ["DYNAMODB_TABLE_NAME"] = "client-tracking-data"
    # Crear tabla con solo HASH key "ID"
    ddb = boto3.resource("dynamodb", region_name=region)
    ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "ID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "ID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )
    table = ddb.Table(TABLE_NAME)

    # 2) Insertar un ítem dentro del rango
    item = {
        "ID": "abc123",
        "DateUTC": "2025-07-01T12:00:00Z",
        "IP": "1.2.3.4",
        "MAC": "AA:BB:CC:DD",
        "Device": "Phone"
    }
    table.put_item(Item=item)

    # 3) Ejecutar fetch y comprobar
    syncer = DeviceDdbSyncer()
    results = list(syncer.fetch("2025-07-01T00:00:00Z", "2025-07-02T00:00:00Z", limit=10))

    assert len(results) == 1
    device: Device = results[0]
    assert isinstance(device, Device)
    assert device.MAC == "AA:BB:CC:DD"
    assert device.Date == "2025-07-01T12:00:00Z"
    assert device.id is None  # debe ser None para dejar que ES genere el _id

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

    # Insertar varios ítems (> limit)
    for i in range(15):
        table.put_item(Item={
            "ID": f"id-{i}",
            "DateUTC": "2025-07-01T12:00:00Z",
            "IP": f"1.2.3.{i}",
            "MAC": f"AA:BB:CC:{i:02X}"
        })

    # Monkeypatch para forzar limit=5
    syncer = DeviceDdbSyncer()
    results = list(syncer.fetch("2025-07-01T00:00:00Z", "2025-07-02T00:00:00Z", limit=5))
    # Debería devolver 15 items en total, a pesar del limit interno por página
    assert len(results) == 15

