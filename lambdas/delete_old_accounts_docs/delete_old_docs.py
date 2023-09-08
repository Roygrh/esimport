import requests
import os
import logging
from datetime import datetime
from requests_aws_sign import AWSV4Sign
from boto3 import session
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries
from datadog_api_client.v2.model.metric_resource import MetricResource
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType

ES_HOST = os.environ.get("ELASTICSEARCH_HOST", "http://localhost:9200")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
DD_API_KEY = os.environ.get("DD_API_KEY",None)
IDX_NAME = os.environ.get("INDEX_NAME", None)
AWS_REGION = os.environ.get("AWS_REGION",None)

FORMAT = "[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(lineno)s:\t%(message)s\n"
logger = logging.getLogger("archive_expired_accounts")
logger.setLevel(LOG_LEVEL)

for handler in logger.handlers:
    handler.setFormatter(logging.Formatter(FORMAT))


def delete_docs_lambda_handler(event, context):
    """
        Lambda handler to start delete operation
    """
    if IDX_NAME is None:
        raise Exception('Specify index name with INDEX_NAME env variable')

    try:
        response = delete_docs()
        submit_step_machine_metric(0)
        return response
    except Exception as err:
        submit_step_machine_metric(1)
        logger.exception(err)
        raise


def delete_docs():
    """
        Start the delete docs operation. We use task api so we don't wait for
        delete operation to complete.
    """
    logger.info(f"Deleting old account docs")
    payload = {
        "query": {
            "bool": {
                "filter": [
                    {"terms": {"Status": ["Deleted", "Expired", "Removed"]}},
                    {"range": {"DateModifiedUTC": {"lt": "now-18M-1d"}}},
                ]
            }
        }
    }

    url = ES_HOST + f"/{IDX_NAME}/_delete_by_query"
    params = {"wait_for_completion": "false"}
    response = requests.post(url, json=payload, params=params, auth=get_auth())
    response = response.json()
    return response


def check_task_status_lambda_handler(event, context):
    """
        Lambda handler for to check task status
    """
    try:
        response = check_task_status(event, context)
        submit_step_machine_metric(0)
        return response
    except Exception as e:
        submit_step_machine_metric(1)
        logger.exception(e)
        raise

def check_task_status(event, context):
    """
        we use elasticsearch tasks api to asyncrously perform delete op.
        we check the delete operation status and handle response accordingly
    """
    task = event.get("task")
    url = ES_HOST + "/_tasks/" + task
    response = requests.get(url, auth=get_auth())
    response = response.json()
    if response['response']['failures'] or response['response']['error']:
        raise Exception(f"error in delete operation {response}")
    response["task"] = task
    return response


def get_auth():
    """
        Get auth credentials to sign elasticsearch requests with AuthV4
    """
    sess = session.Session()
    credentials = sess.get_credentials()
    region = sess.region_name
    service = "es"

    return AWSV4Sign(credentials, region, service)

def submit_step_machine_metric(value=1):
    """
        Submit metric to datadog.
        
        :param value: 0 means an success, 1 means error

    """
    configuration = Configuration()
    configuration.api_key["apiKeyAuth"] = DD_API_KEY
    api_client = ApiClient(configuration)
    instance = MetricsApi(api_client)
    body = MetricPayload(
        series=[
            MetricSeries(
                metric="esimport.step_machine.delete_docs_failed_step_machine",
                type=MetricIntakeType.COUNT,
                unit="err",
                points=[MetricPoint(timestamp=int(datetime.utcnow().timestamp()),value=value)],
                resources=[MetricResource(name=AWS_REGION,type="host")],
            )
        ])
    return instance.submit_metrics(body)
