import os
from dotenv import load_dotenv
import boto3

# load .env locally (if it exists)
load_dotenv()

# switch between SQL and DynamoDB
USE_DDB_DEVICES = os.getenv("USE_DDB_DEVICES", "false").lower() == "true"

# DynamoDB table name
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "client-tracking-data")

# AWS region (fall back to Boto3 default)
AWS_REGION = os.getenv("AWS_REGION", boto3.Session().region_name)

# SNS topic ARN to trigger indexing in ES via Lambda
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")

# SQL connection (fallback)
SQL_CONNECTION_STRING = os.getenv("SQL_CONNECTION_STRING", "")