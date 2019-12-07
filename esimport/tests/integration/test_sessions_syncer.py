from datetime import datetime
from time import sleep

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import SessionsSyncer

from esimport.tests.base_fixtures import sqs


def test_account_syncer(sqs):
    ss = SessionsSyncer()
    ss.setup()
    ss.resume(1, datetime(2000, 1, 1), False)
    ss.resume(1, datetime(2000, 1, 1), True)

    ss.sns_buffer._flush()

    sqs_msgs = sqs.receive_messages(
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
        VisibilityTimeout=15,
        WaitTimeSeconds=20,
        MaxNumberOfMessages=1,
    )
    topic = ss.aws.sns_resource.Topic(ss.config.sns_topic_arn)
    topic.delete()
    sqs.delete()
    assert len(sqs_msgs) != 0
