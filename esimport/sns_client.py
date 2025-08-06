# esimport/sns_client.py
import json
import boto3
from esimport.config import SNS_TOPIC_ARN, AWS_REGION

_sns = boto3.client("sns", region_name=AWS_REGION)

def publish_batch(records: list):
    """
    Publish a JSON message with the list of documents to SNS.
    The subscribed Lambda (sqs_consumer) will be responsible for indexing in ES.
    """
    if not SNS_TOPIC_ARN:
        raise RuntimeError("SNS_TOPIC_ARN is not set")
    payload = [r._source for r in records]
    _sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(payload),
    )