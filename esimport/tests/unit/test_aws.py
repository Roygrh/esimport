import boto3
import pytest
from time import sleep
from esimport.core import Config
from esimport.tests.base_fixutres import (
    dynamodb_client,
    latest_ids_table,
    empty_table,
    sns_client,
)

from esimport.infra import AmazonWebServices


def test_aws(latest_ids_table):

    config = Config()

    ports_mappings = {
        "s3": config.s3_port,
        "sns": config.sns_port,
        "dynamodb": config.dynamodb_port,
    }

    aws = AmazonWebServices(
        endpoint_url=config.aws_endpoint_url,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.aws_default_region,
        ports_mappings=ports_mappings,
    )

    aws.create_sns_topic("test_topic")
    aws.create_dynamodb_table("latest_ids")
    # allow the table to be created
    sleep(2)
    latest_ids_table.put_item(Item={"doctype": "account"})
