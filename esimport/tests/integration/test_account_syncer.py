from datetime import datetime
from time import sleep

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import AccountsSyncer

from esimport.tests.base_fixtures import sqs


def test_account_syncer_by_id(sqs):
    ac = AccountsSyncer()
    ac.setup()

    # if tabele is already there it passes silently
    ac.aws.create_dynamodb_table(ac.config.dynamodb_table)
    # allow the table to be created
    sleep(2)
    ac.put_item_in_dynamodb_table("account", 0, datetime(2019, 1, 1))
    ac.update(datetime(2019, 1, 1))
    ac.process_accounts_from_id(2, "2000-01-01")

    ac.sns_buffer._flush()

    sqs_msgs = sqs.receive_messages(
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
        VisibilityTimeout=15,
        WaitTimeSeconds=20,
        MaxNumberOfMessages=1,
    )
    topic = ac.aws.sns_resource.Topic(ac.config.sns_topic_arn)
    topic.delete()
    sqs.delete()
    assert len(sqs_msgs) != 0


def test_account_syncer_by_period(sqs):
    ac = AccountsSyncer()
    ac.setup()

    # if tabele is already there it passes silently
    ac.aws.create_dynamodb_table(ac.config.dynamodb_table)
    # allow the table to be created
    sleep(2)
    ac.process_accounts_in_period(datetime(2000, 1, 1), datetime(2019, 1, 1))

    ac.sns_buffer._flush()

    sqs_msgs = sqs.receive_messages(
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
        VisibilityTimeout=15,
        WaitTimeSeconds=20,
        MaxNumberOfMessages=1,
    )
    topic = ac.aws.sns_resource.Topic(ac.config.sns_topic_arn)
    topic.delete()
    sqs.delete()
    assert len(sqs_msgs) != 0
