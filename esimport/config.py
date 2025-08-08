import os
from dotenv import load_dotenv
import boto3

# load .env locally (if it exists)
load_dotenv()

# DynamoDB table name
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")

# AWS region (fall back to Boto3 default)
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", boto3.Session().region_name)

# DynamoDB scan/query page size
DDB_QUERY_LIMIT = int(os.getenv("DDB_QUERY_LIMIT", "1000"))

# SNS topic ARN to trigger indexing in ES via Lambda
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")