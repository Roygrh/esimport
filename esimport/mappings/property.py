################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import time
import pprint
import logging

from elasticsearch import Elasticsearch
from elasticsearch import exceptions

from esimport.utils import retry
from esimport import settings
from esimport.models.property import Property
from esimport.connectors.mssql import MsSQLConnector
from esimport.mappings.doc import DocumentMapping
from esimport.cache import CacheClient
from extensions import sentry_client

logger = logging.getLogger(__name__)


class PropertyMapping(DocumentMapping):
    model = None
    es = None

    def __init__(self):
        super(PropertyMapping, self).__init__()

    def setup(self):
        logger.debug("Setting up DB connection")
        conn = MsSQLConnector()
        self.model = Property(conn)

        logger.debug("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)
        self.cache_client = CacheClient()

    """
    Add Properties from SQL into ElasticSearch
    """

    def sync(self):
        while True:
            count = 0
            start = self.max_id()
            for prop in self.model.get_properties(start, self.step_size):
                count += 1
                logger.debug("Record found: {0}".format(prop.get('ID')))
                self.add(dict(prop.es()), self.step_size)

            # for cases when all/remaining items count were less than limit
            self.add(None, min(len(self._items), self.step_size))

            # only wait between DB calls when there is no delay from ES (HTTP requests)
            if count <= 0:
                logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
                time.sleep(self.db_wait)

    """
    Find existing property records in ElasticSearch
    """

    def get_existing_properties(self, start, limit):
        logger.debug("Fetching {0} records from ES where ID >= {1}" \
                     .format(limit, start))
        records = self.es.search(index=settings.ES_INDEX, doc_type=Property.get_type(),
                                 sort="ID:asc", size=limit,
                                 q="ID:[{0} TO *]".format(start))
        for record in records['hits']['hits']:
            yield record.get('_source')

    """
    Continuously update ElasticSearch to have the latest Property data
    """

    def update(self):
        start = 0
        while True:
            count = 0
            for prop in self.model.get_properties(start, self.step_size):
                count += 1
                logger.debug("Record found: {0}".format(prop.get('ID')))

                for service_area in prop.get('ServiceAreas'):
                    self.cache_client.set(service_area, prop.record)

                self.add(dict(prop.es()), self.step_size)
                start = prop.record.get('ID')

            # for cases when all/remaining items count were less than limit
            self.add(None, min(len(self._items), self.step_size))

            # always wait between DB calls
            time.sleep(self.db_wait)

            if count <= 0:
                start = 0
                time.sleep(self.db_wait * 4)

    """
    Use ElasticSearch Property data to find the site associated with a service area
    """

    @retry(settings.ES_RETRIES, settings.ES_RETRIES_WAIT)
    def get_properties_by_service_area(self, service_area):
        try:
            record = self.cache_client.get(service_area)
        except Exception:
            record = None
            sentry_client.captureException()

        if record is not None:
            logger.debug("Fetched record from cache for Service Area: {0}.".format(service_area))
            yield record
        else:
            logger.debug("Fetching records from ES where Service Area: {0} exists." \
                        .format(service_area))
            records = self.es.search(index=settings.ES_INDEX, doc_type=Property.get_type(),
                                    body={
                                        "query": {
                                            "match": {
                                                "ServiceAreas": service_area
                                            }
                                        }
                                    })
            for record in records['hits']['hits']:
                yield record.get('_source')

        logger.warning("Property Service Area match not found for {0}".format(
            service_area))


    def backload(self):
        start = 0
        for prop in self.model.get_properties(start, self.step_size):
            p = prop.es()
            logger.debug("Record found: {0}".format(prop.get('ID')))
            self.add(dict(p), self.step_size)

            # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))