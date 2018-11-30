################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import time
import logging
from datetime import timezone

from esimport.utils import convert_utc_to_local_time, set_utc_timezone
from esimport.models.device import Device
from esimport.mappings.appended_doc import PropertyAppendedDocumentMapping
from esimport import settings

logger = logging.getLogger(__name__)


class DeviceMapping(PropertyAppendedDocumentMapping):

    dates_to_localize = (
        ('DateUTC', 'DateLocal'),)

    def __init__(self):
        super(DeviceMapping, self).__init__()

    def setup(self):  # pragma: no cover
        super(DeviceMapping, self).setup()
        self.model = Device(self.conn)

    @staticmethod
    def get_monitoring_metric():
        return settings.DATADOG_DEVICE_METRIC

    """
    Loop to continuously find new Devices and add them to Elasticsearch
    """
    def sync(self, start_date):
        start = self.max_id() + 1
        timer_start = time.time()
        while True:
            count = 0
            metric_value = None

            logger.debug("Get Devices from {0} to {1} since {2}"
                .format(start, start+self.step_size, start_date))

            for device in self.model.get_devices(start, self.step_size, start_date):
                count += 1
                logger.debug("Record found: {0}".format(device.get('ID')))

                _action = super(DeviceMapping, self).get_site_values(device.get('ServiceArea'))

                if 'TimeZone' in _action:
                    for pfik, pfiv in self.dates_to_localize:
                        _action[pfiv] = convert_utc_to_local_time(device.get(pfik), _action['TimeZone'])

                device.update(_action)
                metric_value = device.get(self.model.get_key_date_field())

                self.add(device.es(), self.step_size, metric_value)
                start = device.get('ID') + 1

            # for cases when all/remaining items count were less than limit
            self.add(None, 0, metric_value)

            elapsed_time = int(time.time() - timer_start)

            # habitually reset mssql connection.
            if count == 0 or elapsed_time >= self.db_conn_reset_limit:
                logger.info("[Delay] Reset SQL connection and waiting {0} seconds".format(self.db_wait))
                self.model.conn.reset()
                time.sleep(self.db_wait)
                timer_start=time.time() # reset timer            
