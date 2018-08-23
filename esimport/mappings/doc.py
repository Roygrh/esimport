################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import sys
import time
import pprint
import logging
import traceback
import requests
from datetime import datetime
from dateutil import parser
from datadog import initialize, api

from elasticsearch import Elasticsearch

from elasticsearch import helpers
from elasticsearch import exceptions

from esimport import settings
from esimport.utils import retry
from esimport.connectors.mssql import MsSQLConnector
from esimport.models.account import Account
from esimport.models.conference import Conference
from esimport.models.device import Device
from esimport.models.property import Property
from esimport.models.session import Session

from extensions import sentry_client

logger = logging.getLogger(__name__)


class DocumentMapping(object):
    step_size = None
    esTimeout = None
    esRetry = None

    model = None
    es = None

    conn = None
    _items = None

    def __init__(self):
        self._items = list()

        self.pp = pprint.PrettyPrinter(indent=2, depth=10)  # pragma: no cover
        self.step_size = settings.ES_BULK_LIMIT
        self.esTimeout = settings.ES_TIMEOUT
        self.esRetry = settings.ES_RETRIES
        self.db_wait = settings.DATABASE_CALLS_WAIT
        self.db_record_limit = settings.DATABASE_RECORD_LIMIT

    def setup(self, heartbeat_ping=None):  # pragma: no cover
        logger.info("Setting up DB connection")
        self.conn = MsSQLConnector()
        self.heartbeat_ping = heartbeat_ping

        logger.info("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

    @retry(settings.ES_RETRIES, settings.ES_RETRIES_WAIT, retry_exception=exceptions.ConnectionError)
    def max_id(self):
        logger.debug("Finding max id from index: %s, type: %s" % (
            settings.ES_INDEX, self.model.get_type()))
        filters = dict(index=settings.ES_INDEX, doc_type=self.model.get_type(),
                       body={
                           "aggs": {
                               "max_id": {
                                   "max": {
                                       "field": "ID"
                                   }
                               }
                           },
                           "size": 0
                       })
        response = self.es.search(**filters)
        try:
            _id = response['aggregations']['max_id']['value']
            if _id:
                return int(_id)
        except Exception as err:
            logger.error(err)
            traceback.print_exc(file=sys.stdout)
            sentry_client.captureException()
        return 0

    # FIXME: remove this method and put retry in what's calling it
    @retry(settings.ES_RETRIES, settings.ES_RETRIES_WAIT, retry_exception=exceptions.ConnectionError)
    def bulk_add_or_update(self, es, actions, retries=settings.ES_RETRIES, timeout=settings.ES_TIMEOUT):
        result = helpers.bulk(es, actions, request_timeout=timeout)
        if self.heartbeat_ping and result[0] > 0:
            requests.get(self.heartbeat_ping)

    @retry(settings.ES_RETRIES, settings.ES_RETRIES_WAIT, retry_exception=exceptions.ConnectionError)
    def get_es_count(self):
        logger.debug("Finding records count from index: %s, type: %s" % (
            settings.ES_INDEX, self.model.get_type()))
        filters = dict(index=settings.ES_INDEX, doc_type=self.model.get_type())
        response = self.es.count(**filters)
        try:
            return response['count']
        except Exception as err:
            logger.error(err)
            traceback.print_exc(file=sys.stdout)
            sentry_client.captureException()
        return 0

    def add(self, item, limit):
        if item:
            self._items.append(item)
        items_count = len(self._items)
        if items_count > 0 and items_count >= limit:
            logger.info("Adding/Updating {0} records".format(items_count))
            self.bulk_add_or_update(self.es, self._items)
            self._items = []

    """
    Get the most recent date requested from elasticsearch
    """
    def get_most_recent_date(self, date_field, doc_type):
        q = {
                "query": {
                    "match_all": {}
                },
                "sort":[
                    {
                        str(date_field): {
                            "order": "desc",
                            "missing": "_last",
                            "unmapped_type": "date"
                        }
                    }
                ],
                "size": 1
        }

        try:
            hits = self.es.search(index=settings.ES_INDEX, doc_type=doc_type, body=q)['hits']['hits']
            initial_time = parser.parse(hits[0]['_source'][date_field])
        except Exception as err:
            initial_time = None
            logger.error(err)
            traceback.print_exc(file=sys.stdout)
            sentry_client.captureException()

        return initial_time

    """
    Gets the most recent account record from Elasticsearch and sends the time difference (in minutes)
    between utc now and date of the recent record to datadog
    """
    def monitor_metric(self):
        if not settings.DATADOG_API_KEY:
            logger.error('ESDataCheck - DataDog API key not found.  Metrics will not be reported to DataDog.')
            return

        # doc_types = {
        #     Account.get_type(): ['DateModifiedUTC', settings.DATADOG_ACCOUNT_METRIC],
        #     Conference.get_type(): ['UpdateTime', settings.DATADOG_CONFERENCE_METRIC],
        #     Device.get_type(): ['DateUTC', settings.DATADOG_DEVICE_METRIC],
        #     Property.get_type(): ['UpdateTime', settings.DATADOG_PROPERTY_METRIC],
        #     Session.get_type(): ['LogoutTime', settings.DATADOG_SESSION_METRIC]
        # }

        initialize(api_key=settings.DATADOG_API_KEY, host_name=settings.ENVIRONMENT)

        doc_type = self.model.get_type()
        date_field = self.model.get_key_date_field()
        metric_setting = self.get_monitoring_metric()

        while True:
            # for doc_type, date_field_settings in doc_types.items():
            recent_date = self.get_most_recent_date(date_field, doc_type)
            if recent_date is not None:
                now = datetime.utcnow()
                minutes_behind = (now - recent_date).total_seconds() / 60
                api.Metric.send(metric=metric_setting, points=minutes_behind)
                logger.debug('ESDataCheck - Host: {0} - Metric: {1} - Minutes Behind: {2:.2f} - Now: {3}'.format(settings.ENVIRONMENT, 
                                                                                                                metric_setting, 
                                                                                                                minutes_behind, 
                                                                                                                now))
            else:
                logger.error('ESDataCheck - Unable to determine the most recent account record by {}'.format(doc_type))
            
            time.sleep(15)
