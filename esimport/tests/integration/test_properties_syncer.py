from datetime import datetime
from time import sleep

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import PropertiesSyncer

from esimport.tests.base_fixtures import sqs


def test_session_syncer(sqs):
    ps = PropertiesSyncer()
    ps.setup()

    # if tabele is already there it passes silently
    ps.aws.create_dynamodb_table(ps.config.dynamodb_table)
    # allow the table to be created
    sleep(2)
    ps.process_properties_from_id(1)

    ps.sns_buffer._flush()

    sqs_msgs = sqs.receive_messages(
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
        VisibilityTimeout=15,
        WaitTimeSeconds=20,
        MaxNumberOfMessages=1,
    )
    topic = ps.aws.sns_resource.Topic(ps.config.sns_topic_arn)
    topic.delete()
    sqs.delete()
    assert len(sqs_msgs) != 0

