# HACK: Replacing self.step_size with 50 so other mappings still process the amount
# set in the config, but the property mapping will always use 50 regardless.  This is
# because there is too much data being sent to AWS ES and it's throwing an exception.
# This is a quick hack that should be fixed in a different way.


################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import logging
import time

from esimport import settings
from esimport.mappings.doc import DocumentMapping
from esimport.models.property import Property

logger = logging.getLogger(__name__)


class PropertyMapping(DocumentMapping):
    model = None

    def __init__(self):
        super(PropertyMapping, self).__init__()
        self.default_query_limit = 50

    def setup(self):
        super(PropertyMapping, self).setup()
        self.model = Property(self.conn)
        self._version_date_fieldname = self.model._version_date_fieldname

    @staticmethod
    def get_monitoring_metric():
        return settings.DATADOG_PROPERTY_METRIC

    def process_properties_from_id(self, latest_processed_id: int) -> (int, int):
        count = 0
        metric_value = None
        for prop in self.model.get_properties(latest_processed_id, self.default_query_limit):
            count += 1
            logger.debug("Record found: {0}".format(prop.get('ID')))

            # add both Property/Organization Number and Service Areas to the cache
            self.cache_client.set(prop.get('Number'), prop.record)

            for service_area_obj in prop.get('ServiceAreaObjects'):
                self.cache_client.set(service_area_obj['Number'], prop.record)

            metric_value = prop.get(self.model.get_key_date_field())

            self.add(prop.es(), metric_value)
            latest_processed_id = prop.record.get('ID')

        # for cases when all/remaining items count were less than limit
        self.add(None, metric_value)
        return count, latest_processed_id

    """
    Continuously update ElasticSearch to have the latest Property data
    """
    def update(self):
        latest_processed_id = 0
        timer_start = time.time()
        while True:
            count, latest_processed_id = self.process_properties_from_id(latest_processed_id)
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
                    latest_processed_id = 0

    def get_property_by_org_number(self, org_number):
        # TODO add direct test for it

        if self.cache_client.exists(org_number):
            logger.debug("Fetching record from cache for Org Number: {0}.".format(org_number))
            return self.cache_client.get(org_number)
        else:
            logger.info("Fetching record from DB for Org Number: {0}.".format(org_number))
            record = self.model.get_property_by_org_number(org_number)

            if record is None:
                msg = "Property not found for Org Number: {0}.  Updating cache with a null object"
                logger.warning(msg.format(org_number))
            else:
                record = record.get('_source')

            # set the property in the cache.  If the object is null, then this will create a key
            # for this org number and this will be how we know not to continually go back to ES
            # for data that doesn't exist.  The ESImport process for properties will overwrite
            # this cache entry with the correct object.
            self.cache_client.set(org_number, record)
            return record

