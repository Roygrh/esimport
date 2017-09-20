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

from elasticsearch import Elasticsearch

from elasticsearch import helpers
from elasticsearch import exceptions

from esimport import settings
from esimport.utils import retry
from esimport.connectors.mssql import MsSQLConnector

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

    def setup(self):  # pragma: no cover
        logger.debug("Setting up DB connection")
        self.conn = MsSQLConnector()

        logger.debug("Setting up ES connection")
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
        helpers.bulk(es, actions, request_timeout=timeout)

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
