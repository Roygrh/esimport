import boto3
import pytest
from time import sleep

from esimport.tests.base_fixutres import (
    dynamodb_client,
    latest_ids_table,
    empty_table,
    sns_client,
)

from esimport.infra import AmazonWebServices


def test_aws(latest_ids_table):
    aws = AmazonWebServices()

    aws.create_sns_topic("test_topic")
    aws.create_dynamodb_table("latest_ids")
    # allow the table to be created
    sleep(2)
    latest_ids_table.put_item(Item={"doctype": "account"})
