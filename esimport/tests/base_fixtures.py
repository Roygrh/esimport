import pytest
import boto3
import os


@pytest.fixture
def sqs():
    session = boto3.session.Session(
        aws_access_key_id="foo",
        aws_secret_access_key="bar",
        region_name="us-west-2",
        profile_name=None,
    )
    sqs_client = session.client("sqs", endpoint_url="http://localhost:4576")

    sns_client = session.client("sns", endpoint_url="http://localhost:4575")

    sqs_obj = session.resource("sqs", endpoint_url="http://localhost:4576")

    sqs_queue_name = "test"

    # Create/Get Queue
    res = sqs_client.create_queue(QueueName=sqs_queue_name)
    sns_client.create_topic(Name="test")
    sqs_queue = sqs_obj.Queue(res["QueueUrl"])
    sqs_queue_attrs = sqs_client.get_queue_attributes(
        QueueUrl=res["QueueUrl"], AttributeNames=["All"]
    )["Attributes"]
    sqs_queue_arn = sqs_queue_attrs["QueueArn"]
    if ":sqs." in sqs_queue_arn:
        sqs_queue_arn = sqs_queue_arn.replace(":sqs.", ":")

    # Subscribe SQS queue to SNS
    sns_client.subscribe(
        TopicArn=os.getenv("SNS_TOPIC_ARN"), Protocol="sqs", Endpoint=sqs_queue_arn
    )

    return sqs_queue


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

