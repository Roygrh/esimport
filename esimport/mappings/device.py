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
from esimport.mappings.appended_doc import PropertyAppendedDocumentMapping
from esimport.models.device import Device

logger = logging.getLogger(__name__)


class DeviceMapping(PropertyAppendedDocumentMapping):

    dates_to_localize = (
        ('DateUTC', 'DateLocal'),)

    def __init__(self):
        super(DeviceMapping, self).__init__()
        self.default_query_limit = 20

    def setup(self):  # pragma: no cover
        super(DeviceMapping, self).setup()
        self.model = Device(self.conn)
        self._version_date_fieldname = self.model._version_date_fieldname

    @staticmethod
    def get_monitoring_metric():
        return settings.DATADOG_DEVICE_METRIC

    def process_devices_from_id(self, next_id_to_process: int, start_date) -> (int, int):
        count = 0
        metric_value = None

        logger.debug("Get Devices from {0} to {1} since {2}".format(
            next_id_to_process, next_id_to_process+self.default_query_limit, start_date
        ))

        for device in self.model.get_devices(next_id_to_process, self.default_query_limit, start_date):
            count += 1
            logger.debug("Record found: {0}".format(device.get('ID')))

            self.update_time_zones(device, device.get('ServiceArea'), self.dates_to_localize)

            metric_value = device.get(self.model.get_key_date_field())

            self.add(device.es(), metric_value)
            next_id_to_process = device.get('ID') + 1

        # for cases when all/remaining items count were less than limit
        self.add(None, metric_value)
        return count, next_id_to_process

    """
    Loop to continuously find new Devices and push them to AWS SQS
    """
    def sync(self, start_date):
        next_id_to_process = self.max_id() + 1
        timer_start = time.time()
        while True:
            count, next_id_to_process = self.process_devices_from_id(next_id_to_process, start_date)

            elapsed_time = int(time.time() - timer_start)

            # habitually reset mssql connection.
            if count == 0 or elapsed_time >= self.db_conn_reset_limit:
                logger.info("[Delay] Reset SQL connection and waiting {0} seconds".format(self.db_wait))
                self.model.conn.reset()
                time.sleep(self.db_wait)
                timer_start = time.time()  # reset timer
