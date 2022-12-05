import pytest
import boto3
import os

from esimport.core import Config


@pytest.fixture
def sqs():
    config = Config()

    session = boto3.session.Session(
        aws_access_key_id="foo",
        aws_secret_access_key="bar",
        region_name="us-west-2",
        profile_name=None,
    )
    sqs_client = session.client(
        "sqs", endpoint_url=f"{config.aws_endpoint_url}:{config.sqs_port}"
    )

    sns_client = session.client(
        "sns", endpoint_url=f"{config.aws_endpoint_url}:{config.sns_port}"
    )

    sqs_obj = session.resource(
        "sqs", endpoint_url=f"{config.aws_endpoint_url}:{config.sqs_port}"
    )

    sqs_queue_name = "test"

    # Create/Get Queue
    res = sqs_client.create_queue(QueueName=sqs_queue_name)
    sns_topic_resp = sns_client.create_topic(Name="test")
    sqs_queue = sqs_obj.Queue(res["QueueUrl"])
    sqs_queue_attrs = sqs_client.get_queue_attributes(
        QueueUrl=res["QueueUrl"], AttributeNames=["All"]
    )["Attributes"]
    sqs_queue_arn = sqs_queue_attrs["QueueArn"]
    if ":sqs." in sqs_queue_arn:
        sqs_queue_arn = sqs_queue_arn.replace(":sqs.", ":")

    # Subscribe SQS queue to SNS
    sns_client.subscribe(
        TopicArn=sns_topic_resp["TopicArn"], Protocol="sqs", Endpoint=sqs_queue_arn
    )

    return sqs_queue


@pytest.fixture
def sqs_dpsk():
    config = Config()
    session = boto3.session.Session(
        aws_access_key_id="foo",
        aws_secret_access_key="bar",
        region_name="us-west-2",
        profile_name=None,
    )
    sqs_client = session.client(
        "sqs", endpoint_url=f"{config.aws_endpoint_url}:{config.sqs_port}"
    )

    sns_client = session.client(
        "sns", endpoint_url=f"{config.aws_endpoint_url}:{config.sns_port}"
    )

    sqs_obj = session.resource(
        "sqs", endpoint_url=f"{config.aws_endpoint_url}:{config.sqs_port}"
    )

    dynamodb_obj = session.resource(
        "dynamodb", endpoint_url=f"{config.aws_endpoint_url}:{config.dynamodb_port}"
    )

    source_sns = sns_client.create_topic(Name="source")
    source_sqs = sqs_client.create_queue(QueueName="source")

    target_sns = sns_client.create_topic(Name="target")
    target_sqs = sqs_client.create_queue(QueueName="target")

    source_sqs_queue = sqs_obj.Queue(source_sqs["QueueUrl"])
    target_sqs_queue = sqs_obj.Queue(target_sqs["QueueUrl"])

    if config.dynamodb_table not in dynamodb_obj.meta.client.list_tables()["TableNames"]:
        dynamodb = dynamodb_obj.create_table(
            AttributeDefinitions=[{"AttributeName": "doctype", "AttributeType": "S"},],
            TableName=config.dynamodb_table,
            KeySchema=[{"AttributeName": "doctype", "KeyType": "HASH"},],
            ProvisionedThroughput={"ReadCapacityUnits": 123, "WriteCapacityUnits": 123},
        )

    source_sqs_attributes = sqs_client.get_queue_attributes(
        QueueUrl=source_sqs["QueueUrl"], AttributeNames=["All"]
    )["Attributes"]

    target_sqs_attributes = sqs_client.get_queue_attributes(
        QueueUrl=target_sqs["QueueUrl"], AttributeNames=["All"]
    )["Attributes"]

    sns_client.subscribe(
        TopicArn=source_sns["TopicArn"],
        Protocol="sqs",
        Endpoint=source_sqs_attributes["QueueArn"],
    )

    sns_client.subscribe(
        TopicArn=target_sns["TopicArn"],
        Protocol="sqs",
        Endpoint=target_sqs_attributes["QueueArn"],
    )

    return target_sqs_queue


"""
    # Publish SNS Messages
    test_msg = {"default": {"x": "foo", "y": "bar"}}
    test_msg_body = json.dumps(test_msg)
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=json.dumps({"default": test_msg_body}),
        MessageStructure="json",
    )

    # Validate Message
    sqs_msgs = sqs_queue.receive_messages(
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
        VisibilityTimeout=15,
        WaitTimeSeconds=20,
        MaxNumberOfMessages=5,
    )
"""

