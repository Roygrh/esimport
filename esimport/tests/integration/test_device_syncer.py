from datetime import datetime
from time import sleep

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import DeviceSyncer

from esimport.tests.base_fixtures import sqs


def test_device_syncer(sqs):
    ds = DeviceSyncer()
    ds.setup()

    # if tabele is already there it passes silently
    ds.aws.create_dynamodb_table(ds.config.dynamodb_table)
    # allow the table to be created
    sleep(2)
    ds.process_devices_from_id(1, "2000-01-01")

    ds.sns_buffer._flush()

    sqs_msgs = sqs.receive_messages(
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
        VisibilityTimeout=15,
        WaitTimeSeconds=20,
        MaxNumberOfMessages=1,
    )
    topic = ds.aws.sns_resource.Topic(ds.config.sns_topic_arn)
    topic.delete()
    sqs.delete()
    assert len(sqs_msgs) != 0

