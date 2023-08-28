import requests, os, logging
from datetime import datetime, timedelta
from requests_aws_sign import AWSV4Sign
from boto3 import session

ES_HOST = os.environ.get("ELASTICSEARCH_HOST","http://localhost:9200")
LOG_LEVEL = os.environ.get("LOG_LEVEL","DEBUG")

IDX_NAME = "accounts-current"
DELETE_DOCS_LT_DAYS=540

FORMAT = "[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(lineno)s:\t%(message)s\n"
logger = logging.getLogger('archive_expired_accounts')
logger.setLevel(LOG_LEVEL)

for handler in logger.handlers:
    handler.setFormatter(logging.Formatter(FORMAT))

def delete_docs_lambda_handler(event, context):
    try:
        delete_docs_lt = datetime.utcnow() - timedelta(days=DELETE_DOCS_LT_DAYS)
        delete_docs_lt = delete_docs_lt.isoformat()
        response = delete_docs(delete_docs_lt)
        return response
    except Exception as err:
        logger.exception(err)
        raise

def delete_docs(delete_docs_lt,index=IDX_NAME):
    logger.info(f"Deleting for docs lt..{delete_docs_lt}")
    payload = {
        "query":{
        "bool":{
            "filter":[
                    {"range":{"Created":{"lte":delete_docs_lt}}}
                ]
                }}}

    url = ES_HOST + f"/{index}/_delete_by_query"
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