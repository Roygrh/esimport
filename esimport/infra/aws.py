import logging
import os
from dataclasses import dataclass
from urllib.parse import urlparse

import boto3

from ._base import BaseInfra


@dataclass
class AmazonWebServices(BaseInfra):
    endpoint_url: str = None
    aws_access_key_id: str = "foo"
    aws_secret_access_key: str = "bar"
    ports_mappings: dict = None
    region_name: str = None
    profile_name: str = None
    logger: logging.Logger = None

    def __post_init__(self):
        # Parse the URL and make sure it's something valid
        # this will fail if the URL is not valid.
        self.aws_endpoint_url = (
            urlparse(self.endpoint_url) if self.endpoint_url else None
        )

        if not self.aws_endpoint_url:
            # If a custom endpoint is not provided, we don't want AWS_ACCESS_KEY
            # nor AWS_SECRET_ACCESS_KEY to interfere. On prod, the permission is assumed by the IAM role
            self.aws_access_key_id = None
            self.aws_secret_access_key = None

        # Construct a base boto3 session to be shared by the different resources
        self.session = boto3.session.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
            profile_name=self.profile_name,
        )

        self._log(
            f"Constructed AWS Session with profile: {self.profile_name} for the region: {self.region_name}.",
            logging.DEBUG,
        )

    def _get_endpoint_url(self, service: str) -> str:
        if self.aws_endpoint_url:
            service_port = self.ports_mappings.get(service)
            endpoint = self.aws_endpoint_url._replace(
                netloc=f"{self.aws_endpoint_url.netloc}:{service_port}"
            ).geturl()
            self._log(
                f"Using endpoint: {endpoint} for the {service} resource.", logging.DEBUG
            )
            return endpoint

        return None

    def _get_service_resource(
        self, service: str
    ) -> boto3.resources.base.ServiceResource:
        endpoint_url = self._get_endpoint_url(service)
        return self.session.resource(service, endpoint_url=endpoint_url)

    @property
    def s3_resource(self):
        if not hasattr(self, "_s3_resource"):
            self._log("Setting up AWS S3 Client")
            self._s3_resource = self._get_service_resource("s3")
        return self._s3_resource

    @property
    def dynamodb_resource(self):
        if not hasattr(self, "_dynamodb_resource"):
            self._log("Setting up AWS DynamoDB Client")
            self._dynamodb_resource = self._get_service_resource("dynamodb")
        return self._dynamodb_resource

    @property
    def sns_resource(self):
        if not hasattr(self, "_sns_resource"):
            self._log("Setting up AWS SNS Client")
            self._sns_resource = self._get_service_resource("sns")
        return self._sns_resource

    @property
    def sqs_client(self):
        if not hasattr(self, "_sqs_resource"):
            self._log("Setting up SQS client")
            self._sqs_resource = self._get_service_resource("sqs")
        return self._sqs_resource.meta.client

    def sqs_receive_messages(self, sqs_queue_url: str, max_number_of_messages: int = 1):
        return self.sqs_client.receive_message(
            QueueUrl=sqs_queue_url,
            AttributeNames=["All"],
            VisibilityTimeout=15,
            WaitTimeSeconds=20,
            MaxNumberOfMessages=max_number_of_messages,
        )

    def sqs_delete_message(self, sqs_queue_url: str, receipt_handle):
        return self.sqs_client.delete_message(
            QueueUrl=sqs_queue_url, ReceiptHandle=receipt_handle
        )

    def sqs_send_mesage(self, queue_url: str, message_body):
        return self.sqs_client.send_message(
            queue_url=queue_url, MessageBody=message_body
        )

    def create_sns_topic(self, topic_name):
        return self.sns_resource.create_topic(Name=topic_name)

    def create_dynamodb_table(self, table_name):
        dynamodb_client = self.dynamodb_resource.meta.client
        return dynamodb_client.create_table(
            AttributeDefinitions=[{"AttributeName": "doctype", "AttributeType": "S"}],
            TableName=table_name,
            KeySchema=[{"AttributeName": "doctype", "KeyType": "HASH"}],
            BillingMode="PROVISIONED",
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
