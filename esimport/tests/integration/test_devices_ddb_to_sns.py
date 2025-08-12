import os
from datetime import datetime, timezone, timedelta
import boto3
from moto import mock_aws

# --- evitar LocalStack cuando usamos moto ---
for var in ("AWS_ENDPOINT_URL", "DYNAMODB_PORT", "S3_PORT", "SNS_PORT", "SQS_PORT"):
    os.environ.pop(var, None)
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["DYNAMODB_TABLE_NAME"] = "client-tracking-data"
os.environ["DDB_QUERY_LIMIT"] = "2"
# -------------------------------------------

from esimport.syncers.devices.syncer import DeviceSyncer
from esimport.core import sync_base as core_sync_base  # para monkeypatch

TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]
REGION = os.environ["AWS_REGION"]

@mock_aws
def test_device_syncer_reads_from_ddb_and_emits_records(monkeypatch):
    # 1) Stub de configuración para que SyncBase.__init__ no explote
    class _DummyCfg:
        aws_endpoint_url = None
        aws_access_key_id = "x"
        aws_secret_access_key = "y"
        aws_default_region = REGION
        s3_port = sns_port = dynamodb_port = sqs_port = None
        redis_host = "localhost"
        redis_port = 6379
        sns_topic_arn = "arn:aws:sns:us-east-1:000000000000:test"
        max_sns_bulk_send_size_in_bytes = 256000
        datadog_api_key = "fake"
        datadog_env = "fake"
        # MSSQL placeholders (no usados en este test)
        mssql_dsn = ""
        database_info = {}
        database_query_timeout = 30
        database_connection_timeout = 30

    monkeypatch.setattr(core_sync_base.SyncBase, "get_config", lambda self: _DummyCfg(), raising=True)
    # 2) Evitar inicialización pesada
    monkeypatch.setattr(core_sync_base.SyncBase, "setup", lambda self: None, raising=True)

    # (Opcional) fijar el índice si no quieres depender del formateo de fecha
    # monkeypatch.setattr(DeviceSyncer, "get_target_elasticsearch_index", lambda self, _: "devices-idx", raising=True)

    # DDB de moto y tabla
    ddb = boto3.client("dynamodb", region_name=REGION)
    ddb.create_table(
        TableName=TABLE_NAME,
        AttributeDefinitions=[{"AttributeName": "ID", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "ID", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )

    now = datetime.now(timezone.utc)
    in_range = (now - timedelta(minutes=1)).isoformat()
    out_range = (now - timedelta(days=2)).isoformat()

    def put(ID, DateISO, **kw):
        item = {
            "ID": {"S": ID},
            "DateUTC": {"S": DateISO},   # usado por el filtro
            "DateTime": {"S": DateISO},  # nombre real del proxy
            "IpAddress": {"S": kw.get("IpAddress", "10.0.0.1")},
            "MacAddress": {"S": kw.get("MacAddress", "aa:bb:cc:dd:ee:ff")},
            "UserAgentRaw": {"S": kw.get("UserAgentRaw", "UA")},
            "ClientDeviceTypeId": {"S": kw.get("ClientDeviceTypeId", "Phone")},
            "PlatformTypeId": {"S": kw.get("PlatformTypeId", "iOS")},
            "BrowserTypeId": {"S": kw.get("BrowserTypeId", "Safari")},
            "MemberName": {"S": kw.get("MemberName", "alice")},
            "MemberID": {"S": kw.get("MemberID", "123")},
            "MemberNumber": {"S": kw.get("MemberNumber", "M001")},
            "OrgNumber": {"S": kw.get("OrgNumber", "SA1")},
            "ZoneType": {"S": kw.get("ZoneType", "public")},
        }
        ddb.put_item(TableName=TABLE_NAME, Item=item)

    put("k_in", in_range)
    put("k_out", out_range)

    # Capturar los Records generados
    captured = []
    def fake_add_record(self, record):
        captured.append(record)
    monkeypatch.setattr(DeviceSyncer, "add_record", fake_add_record, raising=True)

    # Act (no hace falta llamar setup(), ya está no-op)
    syncer = DeviceSyncer()
    syncer.sync(start_date=now - timedelta(minutes=10))

    # Assert
    assert len(captured) == 1
    rec = captured[0]
    assert rec.id is None
    assert rec.body["IP"] == "10.0.0.1"
    assert "DateUTC" in rec.body
    assert isinstance(rec.index, str) and rec.index
