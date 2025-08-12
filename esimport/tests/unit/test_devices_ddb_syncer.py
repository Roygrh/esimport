import os
from datetime import datetime, timezone, timedelta
import boto3
import pytest
from moto import mock_aws
import json

from esimport.syncers.devices.ddb_syncer import DeviceDdbSyncer

# --- IMPORTANT: avoid LocalStack when using moto ---
for var in ("AWS_ENDPOINT_URL", "DYNAMODB_PORT", "S3_PORT", "SNS_PORT", "SQS_PORT"):
    os.environ.pop(var, None)
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
# ---------------------------------------------------

TABLE_NAME = "client-tracking-data"
REGION = "us-east-1"
DYNAMODB_PORT = 4566

@pytest.fixture(autouse=True)
def _env():
    os.environ["AWS_REGION"] = REGION
    os.environ["DYNAMODB_TABLE_NAME"] = TABLE_NAME
    os.environ["DDB_QUERY_LIMIT"] = "2" # force pagination
    yield
    os.environ.pop("AWS_ENDPOINT_URL", None)
    #os.environ.pop("DYNAMODB_PORT", DYNAMODB_PORT)

@mock_aws
def test_fetch_from_ddb_maps_and_paginates():
    # Arrange: create table and data in DDB
    ddb = boto3.client("dynamodb", region_name=REGION)
    ddb.create_table(
        TableName=TABLE_NAME,
        AttributeDefinitions=[{"AttributeName": "ID", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "ID", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )

    now = datetime.now(timezone.utc)
    in_range_1 = (now - timedelta(minutes=5)).isoformat()
    in_range_2 = (now - timedelta(minutes=3)).isoformat()
    out_range = (now - timedelta(days=2)).isoformat()

    def put(ID, DateUTC, **kw):
        item = {
            "ID": {"S": ID},
            "DateTime": {"S": DateUTC},
            "IpAddress": {"S": kw.get("IpAddress", "1.2.3.4")},
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

    put("k1", in_range_1)
    put("k2", in_range_2)
    put("k3", out_range)

    # Act
    helper = DeviceDdbSyncer(region=REGION, table_name=TABLE_NAME, query_limit=2)
    docs = list(helper.fetch_from_ddb(start_dt=now - timedelta(minutes=10), end_dt=now))

    # Assert: only 2 in range and with expected fields
    assert len(docs) == 2

    for doc in docs:
        # doc comes from DeviceSchema.dict() (or direct item), without 'id'
        assert "DateUTC" in doc and isinstance(doc["DateUTC"], str)
        assert "IP" in doc and "MAC" in doc
        assert "id" not in doc  # we don't want the id field in the _source

    # --- PRINT: mostrar los 2 documentos obtenidos (ejecuta con `-s` o `-rP`) ---
    print("\nFetched device docs (count={}):".format(len(docs)))
    print(json.dumps(docs, indent=2, ensure_ascii=False))
    # -----------------------------------------------------------------------------
