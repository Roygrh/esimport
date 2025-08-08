import os
from datetime import datetime, timezone, timedelta
import boto3
import pytest
from moto import mock_aws

from esimport.syncers.devices.ddb_syncer import DeviceDdbSyncer

TABLE_NAME = "client-tracking-data"
REGION = "us-east-1"

@pytest.fixture(autouse=True)
def _env():
    os.environ["AWS_REGION"] = REGION
    os.environ["DYNAMODB_TABLE_NAME"] = TABLE_NAME
    os.environ["DDB_QUERY_LIMIT"] = "2" # force pagination
    yield
    os.environ.pop("AWS_REGION", None)
    os.environ.pop("DYNAMODB_TABLE_NAME", None)
    os.environ.pop("DDB_QUERY_LIMIT", None)

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
            "DateUTC": {"S": DateUTC},
            "IP": {"S": kw.get("IP", "1.2.3.4")},
            "MAC": {"S": kw.get("MAC", "aa:bb:cc:dd:ee:ff")},
            "UserAgentRaw": {"S": kw.get("UserAgentRaw", "UA")},
            "Device": {"S": kw.get("Device", "Phone")},
            "Platform": {"S": kw.get("Platform", "iOS")},
            "Browser": {"S": kw.get("Browser", "Safari")},
            "Username": {"S": kw.get("Username", "alice")},
            "MemberID": {"S": kw.get("MemberID", "123")},
            "MemberNumber": {"S": kw.get("MemberNumber", "M001")},
            "ServiceArea": {"S": kw.get("ServiceArea", "SA1")},
            "ZoneType": {"S": kw.get("ZoneType", "public")},
        }
        ddb.put_item(TableName=TABLE_NAME, Item=item)

    put("k1", in_range_1)
    put("k2", in_range_2)
    put("k3", out_range)

    # Act
    helper = DeviceDdbSyncer()
    docs = list(helper.fetch_from_ddb(start_dt=now - timedelta(minutes=10), end_dt=now))

    # Assert: only 2 in range and with expected fields
    assert len(docs) == 2
    for doc in docs:
        # doc comes from DeviceSchema.dict() (or direct item), without 'id'
        assert "DateUTC" in doc and isinstance(doc["DateUTC"], str)
        assert "IP" in doc and "MAC" in doc
        assert "id" not in doc  # we don't want the id field in the _source
