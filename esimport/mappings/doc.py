################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import json
import logging
import pprint
import time
from datetime import datetime
from hashlib import md5  # it is safe only to check that SQS correctly received message

import boto3
from datadog import initialize, api
from dateutil import parser

from esimport import settings
from esimport.cache import CacheClient
from esimport.connectors.mssql import MsSQLConnector

logger = logging.getLogger(__name__)


class OperationalError(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors


class DocumentMapping(object):
    model = None
    cache_client = None
    conn = None
    _items = None

    def __init__(self):
        self.dyndb_table_name = 'latest_ids'
        self._version_date_fieldname = None
        self.init_sqs_connection()
        self._items = list()

        self.pp = pprint.PrettyPrinter(indent=2, depth=10)  # pragma: no cover
        self.db_wait = settings.DATABASE_CALLS_WAIT
        self.db_conn_reset_limit = settings.DATABASE_CONNECTION_RESET_LIMIT
        self.db_record_limit = settings.DATABASE_RECORD_LIMIT
        self.current_size = 0
        self.max_size = settings.MAX_SQL_MSG_SIZE
        self.sqs_session = None
        self.sqs_client = None
        self.dynadmodb_session = None
        self.dynamodb_client = None
        self.sqs_url = settings.SQS_URL

        self.init_sqs_connection()
        self.init_dynamodb_connection()


    def init_sqs_connection(self):
        sqs_endpoint = getattr(settings, 'SQS_ENDPOINT', None)
        if sqs_endpoint is not None:
            self.sqs_session = boto3.session.Session()
            self.sqs_client = self.sqs_session.client(
                service_name='sqs',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY', None),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                region_name=getattr(settings, 'AWS_REGION_NAME', None),
                endpoint_url=sqs_endpoint,
            )
            return
        else:
            self.sqs_client = boto3.client('sqs')

    def init_dynamodb_connection(self):
        dynamodb_endpoint = getattr(settings, 'DYNAMODB_ENDPOINT', None)
        if dynamodb_endpoint is not None:
            self.dynadmodb_session = boto3.session.Session()
            self.dynamodb_table = self.dynadmodb_session.resource(
                service_name='dynamodb',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY', None),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                region_name=getattr(settings, 'AWS_REGION_NAME', None),
                endpoint_url=dynamodb_endpoint,
            ).Table(self.dyndb_table_name)
            return
        else:
            self.dynamodb_table = boto3.resource('dynamodb').Table(self.dyndb_table_name)

    def save_latest_id(self, latest_id: int, latest_date: str):
        response = self.dynamodb_table.put_item(
            Item={
                'doctype': self.model._type, #TODO: replace with method
                "latest_id": latest_id,
                "latest_date": latest_date,
            }
        )

    def setup(self):  # pragma: no cover
        self.conn = MsSQLConnector()
        self.cache_client = CacheClient()

    def put_msg_in_q(self):
        # Intentionally not handling any exceptions
        # if some operation will fail, latest id will not be updated in DynamoDB and next run of application
        # will process records that was not fully processed.

        logger.info("Adding/Updating {0} records".format(len(self._items)))
        msg = '\n'.join(self._items)
        response = self.sqs_client.send_message(
            QueueUrl=self.sqs_url,
            MessageBody=msg,
        )
        sqs_md5 = response.get('MD5OfMessageBody')
        expected_md5 = md5()
        expected_md5.update(msg.encode('utf-8'))

        if sqs_md5 is None or sqs_md5 != expected_md5.hexdigest():
            raise OperationalError('SQS did not received message')

        latest_item = json.loads(self._items[-1])

        latest_id = latest_item['_source']['ID']
        latest_date = latest_item['_source'][self._version_date_fieldname]

        self.save_latest_id(latest_id, latest_date)

        self._items = []
        self.current_size = 0

    def somethings_metric(self, metric_value):
        if metric_value is not None:
            self.cache_client.set(self.get_monitoring_metric(), metric_value)

    def max_id(self):
        response = self.dynamodb_table.get_item(
            TableName=self.dyndb_table_name,
            Key={'doctype': self.model._type},
            ConsistentRead=True,
        )

        return response['Item'].get('latest_id', 0)

    def latest_date(self):
        response = self.dynamodb_table.get_item(
            TableName=self.dyndb_table_name,
            Key={'doctype': self.model._type},
            ConsistentRead=True,
        )

        return response['Item'].get('latest_date', '1900-01-01')

    def add(self, item, metric_value=None):
        """ limit - deprecated and not used """

        if item is None:
            self.put_msg_in_q()
            self.somethings_metric(metric_value)
            return

        json_repr = json.dumps(item)
        bytes_size = len(json_repr.encode('utf-8'))

        if self.current_size + bytes_size < self.max_size:
            self._items.append(json_repr)
            self.current_size += bytes_size
            return
        else:
            self.put_msg_in_q()
            self.somethings_metric(metric_value)
            self._items.append(json_repr)
            self.current_size += bytes_size
            return

    @staticmethod
    def get_monitoring_metric():
        return ""

    """
    Gets the most recent record from Elasticsearch and sends the time difference (in minutes)
    between utc now and date of the recent record to datadog
    """
    def monitor_metric(self):
        if not settings.DATADOG_API_KEY:
            logger.error('ESDataCheck - DataDog API key not found.  Metrics will not be reported to DataDog.')
            return

        initialize(api_key=settings.DATADOG_API_KEY, host_name=settings.ENVIRONMENT)

        doc_type = self.model.get_type()
        metric_setting = self.get_monitoring_metric()

        while True:
            recent_date = self.cache_client.get(metric_setting)
            if recent_date is not None:
                now = datetime.utcnow()
                recent_date = parser.parse(recent_date, ignoretz=True)
                minutes_behind = (now - recent_date).total_seconds() / 60
                api.Metric.send(metric=metric_setting, points=minutes_behind)
                logger.debug(
                    'ESDataCheck - Host: {0} - Metric: {1} - Minutes Behind: {2:.2f} - Now: {3}'.format(
                        settings.ENVIRONMENT,
                        metric_setting,
                        minutes_behind,
                        now)
                )

            else:
                logger.error('ESDataCheck - {0} metric does not exist in cache.'.format(doc_type))

            time.sleep(15)
