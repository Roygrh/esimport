import json

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import DPSKSessionSyncer

from esimport.tests.base_fixtures import sqs_dpsk
from esimport.core import Config


def test_sessions_dpsk_syncer(sqs_dpsk):
    ss = DPSKSessionSyncer()
    ss.config.sns_topic_arn = "arn:aws:sns:us-west-2:000000000000:target"
    ss.config.max_sns_bulk_send_size_in_bytes = 1000
    ss.setup()

    sns_client = ss.sns_buffer.sns_client

    sns_topic_arn = "arn:aws:sns:us-west-2:000000000000:source"

    msg = [
        {
            "ServiceArea": "UE-531-28",
            "UserName": "DSSPSTAFF",
            "NasIdentifier": "uu-423-423",
            "CalledStation": "08-ab-ba-f3-c9-ae",
            "VLAN": "1019",
            "MacAddress": "e9-af-56-49-b2-a7",
            "LoginTime": "2020-03-05T02:22:46.143820+00:00",
            "LogoutTime": "2020-03-05T07:22:46.143820+00:00",
            "ResidentID": "91527d44-d779-4053-a369-5d44ea8b7f4e",
            "SessionID": "Q4YTIBGA-TNOZBSXH",
            "SessionLength": 5756,
            "BytesOut": 8214757314,
            "BytesIn": 740511,
            "TerminationReason": "Lost-Service",
        }
    ]

    _response = sns_client.publish(TopicArn=sns_topic_arn, Message=json.dumps(msg))

    message_id = ss.receive()
    assert message_id, "Got empty message ID"
    assert ss.sns_buffer._last_added_record.id == msg[0]["ResidentID"]
    indexed_msg = ss.sns_buffer._last_added_record._source
    assert indexed_msg["ServiceArea"] == msg[0]["ServiceArea"]

    # Make sure records are being filled up with property info
    property_fields = [
        "PropertyName",
        "PropertyNumber",
        "TimeZone",
        "LoginTimeLocal",
        "LogoutTimeLocal",
    ]

    for field in property_fields:
        assert indexed_msg[field], f"Found {field} missing or with invalid value"
