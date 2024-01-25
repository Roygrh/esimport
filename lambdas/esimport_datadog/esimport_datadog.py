import logging

from datetime import datetime
from datetime import timezone
from datetime import timedelta

from os import environ

import boto3
import datadog
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from urllib3.util import parse_url

from eleven_logging import ElevenFormatter, ExecutorLambdaFormat, FirehoseHandler
import eleven_logging

DATADOG_API_KEY = environ.get("DATADOG_API_KEY")
ENVIRONMENT = environ.get("DATADOG_ENV")
ES_URL = environ.get("ES_URL")
AWS_REGION = environ.get("AWS_DEFAULT_REGION")
LOG_LEVEL = environ.get("LOG_LEVEL")


doc_types = {
    "account": ("accounts-current", "Created", "esimport.account.minutes_behind"),
    "conference": ("conferences", "UpdateTime", "esimport.conference.minutes_behind"),
    "device": ("devices-current", "DateUTC", "esimport.device.minutes_behind"),
    "property": ("properties", "UpdateTime", "esimport.property.minutes_behind"),
    "session": ("sessions-current", "LogoutTime", "esimport.session.minutes_behind"),
    "session-ppk": (
        "sessions-current",
        "LogoutTime",
        "esimport.session-ppk.minutes_behind",
    ),
}

# how far back to look, in minutes
LOOK_BACK_FOR_X_MINUTES = int(environ.get("LOOK_BACK_FOR_X_MINUTES"))

def get_awsauth(region: str, temporary_creds: bool = False) -> AWS4Auth:
    credentials = boto3.Session().get_credentials()
    session_creds = None
    if temporary_creds is True:
        session_creds = credentials.token
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        "es",
        session_token=session_creds,
    )
    return awsauth


def get_signed_es(host: str, awsauth: AWS4Auth) -> Elasticsearch:
    es = Elasticsearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    return es


def parse_es_url(url: str) -> tuple:
    try:
        region = url.split(".")[-4]
        return region, parse_url(url).host
    except Exception as err:
        logger.exception("Check config for ES_URL!!!")
        raise err


class EsimportDatadogLogger:
    def __init__(self):
        datadog.initialize(api_key=DATADOG_API_KEY, host_name=ENVIRONMENT)
        es_region, es_host = parse_es_url(ES_URL)
        awsauth = get_awsauth(es_region, temporary_creds=True)
        self.es = get_signed_es(host=es_host, awsauth=awsauth)

    def process(self):
        try:
            for doc_type, params in doc_types.items():
                index_name, date_field_name, metric_name = params

                result = self.get_last_inserted_doc(
                    self.es,
                    doc_type,
                    index_name,
                    date_field_name,
                    LOOK_BACK_FOR_X_MINUTES,
                )
                now = datetime.now(tz=timezone.utc)
                doc_timedelta = self.extract_doc_datetime(result, date_field_name, now)
                minutes_behind = doc_timedelta.total_seconds() / 60
                self.put_metric(metric_name, minutes_behind, now)
        except Exception as err:
            logger.exception(err)
            raise err

    @staticmethod
    def put_metric(metric_name: str, minutes_behind: float, now: datetime):
        datadog.api.Metric.send(metric=metric_name, points=minutes_behind)
        logger.debug(
            f"ESDataCheck - Host: {ENVIRONMENT} - "
            f"Metric: {metric_name} - Minutes Behind: {minutes_behind:.2f} - Now: {now}"
        )

    @staticmethod
    def get_last_inserted_doc(
        es: Elasticsearch,
        doc_type: str,
        index_name: str,
        date_field: str,
        minutes_behind: int,
    ):
        if doc_type in ["session", "session-ppk"]:
            is_ppk = True if doc_type == "session-ppk" else False
            search_body = {
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"is_ppk": is_ppk}},
                            {
                                "range": {
                                    date_field: {
                                        "gte": f"now-{minutes_behind}m",
                                        "lt": "now",
                                    }
                                }
                            },
                        ]
                    }
                },
                "size": 1,
                "sort": {date_field: "desc"},
            }
        else:
            search_body = {
                "query": {"range": {date_field: {"gte": f"now-{minutes_behind}m"}}},
                "size": 1,
                "sort": {date_field: "desc"},
            }
        result = es.search(index=index_name, body=search_body)
        return result

    @staticmethod
    def extract_doc_datetime(result: dict, date_field_name: str, now: datetime):
        if result["hits"]["total"] == 0:
            return timedelta(minutes=LOOK_BACK_FOR_X_MINUTES)

        field = result["hits"]["hits"][0]["_source"][date_field_name]

        doc_datetime = datetime.fromisoformat(field)

        return now - doc_datetime


def configure_logger(context):
    logger = eleven_logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)
    eleven_formatter = ElevenFormatter(product="esimport",component="esimport_datadog")
    eleven_formatter.set_executor_id_generator(ExecutorLambdaFormat(context=context))
    fh_handler = FirehoseHandler("applog-stream",AWS_REGION)

    fh_handler.setFormatter(eleven_formatter)
    logger.addHandler(fh_handler)
    return logger

esimport_datadog_logger = EsimportDatadogLogger()


def lambda_handler(event, context):
    global logger
    logger = configure_logger(context)
    esimport_datadog_logger.process()
