import requests
import os
import logging
from datetime import datetime, timedelta
from requests_aws_sign import AWSV4Sign
from boto3 import session

ES_HOST = os.environ.get("ELASTICSEARCH_HOST","http://localhost:9200")
LOG_LEVEL = os.environ.get("LOG_LEVEL","DEBUG")

IDX_NAME = "accounts"

FORMAT = "[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(lineno)s:\t%(message)s\n"
logger = logging.getLogger('archive_expired_accounts')
logger.setLevel(LOG_LEVEL)

for handler in logger.handlers:
    handler.setFormatter(logging.Formatter(FORMAT))

def delete_docs_lambda_handler(event, context):
    try:
        return delete_docs()
    except Exception as err:
        logger.exception(err)
        raise

def delete_docs():
    logger.info(f"Deleting old account docs")
    payload = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "bool": {
                            "must_not": [
                                {
                                    "bool": {
                                        "must": [
                                            {"terms": {"Status": [
                                                "Deleted", "Expired", "Removed"]}},
                                            {"range": {"DateModifiedUTC": {
                                                "lte": "now-18M"}}}
                                        ]
                                    }}]
                        }}
                ]}}
    }

    url = ES_HOST + f"/{IDX_NAME}/_delete_by_query"
    params = {"wait_for_completion":"false"}
    response = requests.post(url, json=payload,params=params, auth=get_auth())
    response = response.json()
    return response

def check_task_status_lambda_handler(event, context):
    task = event.get("task")
    url = ES_HOST + "/_tasks/" + task
    response = requests.get(url, auth=get_auth())
    response = response.json()
    response['task'] = task
    return response

def get_auth():
    sess = session.Session()
    credentials = sess.get_credentials()
    region = sess.region_name
    service = 'es'

    return AWSV4Sign(credentials, region, service)