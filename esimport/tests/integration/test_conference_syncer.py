from datetime import datetime
from time import sleep

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import ConferencesSyncer

from esimport.tests.base_fixtures import sqs


def test_conference_syncer(sqs):
    cs = ConferencesSyncer()
    cs.setup()

    # if tabele is already there it passes silently
    cs.aws.create_dynamodb_table(cs.config.dynamodb_table)
    # allow the table to be created
    sleep(2)
    cs.process_conferences_from_id(1, "2000-01-01")

    cs.sns_buffer._flush()

    sqs_msgs = sqs.receive_messages(
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
        VisibilityTimeout=15,
        WaitTimeSeconds=20,
        MaxNumberOfMessages=1,
    )
    topic = cs.aws.sns_resource.Topic(cs.config.sns_topic_arn)
    topic.delete()
    sqs.delete()
    assert len(sqs_msgs) != 0

