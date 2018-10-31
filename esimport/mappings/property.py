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

from elasticsearch import exceptions

from esimport.utils import retry
from esimport import settings
from esimport.models.property import Property
from esimport.connectors.mssql import MsSQLConnector
from esimport.mappings.doc import DocumentMapping
from extensions import sentry_client

logger = logging.getLogger(__name__)


class PropertyMapping(DocumentMapping):
    model = None

    def __init__(self):
        super(PropertyMapping, self).__init__()

    def setup(self):
        super(PropertyMapping, self).setup()
        self.model = Property(self.conn)

    @staticmethod
    def get_monitoring_metric():
        return settings.DATADOG_PROPERTY_METRIC

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
    @retry(settings.ES_RETRIES, settings.ES_RETRIES_WAIT)
    def get_existing_properties(self, start, limit):
        logger.debug("Fetching {0} records from ES where ID >= {1}" \
                     .format(limit, start))
        records = self.es.search(index=settings.ES_INDEX, doc_type=Property.get_type(),
                                 sort="ID:asc", size=limit,
                                 q="ID:[{0} TO *]".format(start), 
                                 request_timeout=60)
        for record in records['hits']['hits']:
            yield record.get('_source')

    """
    Continuously update ElasticSearch to have the latest Property data
    """
    def update(self):
        start = 0
        timer_start=time.time()
        while True:
            count = 0
            metric_value = None
            for prop in self.model.get_properties(start, self.step_size):
                count += 1
                logger.debug("Record found: {0}".format(prop.get('ID')))

                # add both Property/Organization Number and Service Areas to the cache
                self.cache_client.set(prop.get('Number'), prop.record)

                for service_area in prop.get('ServiceAreas'):
                    self.cache_client.set(service_area, prop.record)

                metric_value = prop.get(self.model.get_key_date_field())

                self.add(prop.es(), self.step_size, metric_value)
                start = prop.record.get('ID')

            # for cases when all/remaining items count were less than limit
            self.add(None, 0, metric_value)

            # always wait between DB calls
            logger.info("[Delay] Waiting {0} seconds".format(self.db_wait))
            time.sleep(self.db_wait)

            elapsed_time = int(time.time() - timer_start)

            # habitually reset mssql connection.
            if count == 0 or elapsed_time >= self.db_conn_reset_limit:
                wait = self.db_wait * 2
                logger.info("[Delay] Reset SQL connection and waiting {0} seconds".format(wait))
                self.model.conn.reset()
                time.sleep(wait)
                timer_start=time.time() # reset timer
                # start over again when all records have been processed
                if count == 0:
                    start = 0

    """
    Use ElasticSearch Property data to find the site associated with a organization number
    """
    @retry(settings.ES_RETRIES, settings.ES_RETRIES_WAIT)
    def get_property_by_org_number(self, org_number):

        if self.cache_client.exists(org_number):
            logger.debug("Fetching record from cache for Org Number: {0}.".format(org_number))
            return self.cache_client.get(org_number)
        else:
            # TODO: Fix the query to work with a ServiceAreas array
            es_property_query = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match": {
                                    "Number": org_number
                                }
                            },
                            {
                                "match": {
                                    "ServiceAreas": org_number
                                }
                            }
                        ]
                    }
                }
            }

            logger.info("Fetching record from ES for Org Number: {0}.".format(org_number))
            record = None
            records = self.es.search(index=settings.ES_INDEX, 
                                     doc_type=Property.get_type(), 
                                     size=1, 
                                     body=es_property_query)

            for rec in records['hits']['hits']:
                record = rec.get('_source')

            if record is None:
                msg = "Property not found for Org Number: {0}.  Updating cache with a null object"
                logger.warning(msg.format(org_number))

            # set the property in the cache.  If the object is null, then this will create a key
            # for this org number and this will be how we know not to continually go back to ES
            # for data that doesn't exist.  The ESImport process for properties will overwrite
            # this cache entry with the correct object.
            self.cache_client.set(org_number, record)
            return record

    def backload(self):
        start = 0
        for prop in self.model.get_properties(start, self.step_size):
            p = prop.es()
            logger.debug("Record found: {0}".format(prop.get('ID')))
            self.add(dict(p), self.step_size)

            # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))

    def loadCache(self):
        start = 0
        while True:
            count = 0
            for prop in self.get_existing_properties(start, self.step_size):
                count += 1
                logger.info("Loading property id: {0} into cache".format(prop.get('ID')))

                # add both Property/Organization Number and Service Areas to the cache
                self.cache_client.set(prop.get('Number'), prop)

                for service_area in prop.get('ServiceAreas'):
                    self.cache_client.set(service_area, prop)

                start = prop.get('ID') + 1

            # always wait between ES calls
            logger.info("[Delay] Waiting {0} seconds".format(self.db_wait))
            time.sleep(self.db_wait)

            if count == 0:
                logger.info("All properties have been loaded into cache")
                break
