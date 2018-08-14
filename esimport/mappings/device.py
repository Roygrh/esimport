################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import time
import logging

from esimport.utils import convert_utc_to_local_time, convert_pacific_to_utc
from esimport.models.device import Device
from esimport.mappings.appended_doc import PropertyAppendedDocumentMapping
from esimport import settings

logger = logging.getLogger(__name__)


class DeviceMapping(PropertyAppendedDocumentMapping):
    dates_from_pacific = (('Date', 'DateUTC'),)

    dates_to_localize = (
        ('DateUTC', 'DateLocal'),)

    def __init__(self):
        super(DeviceMapping, self).__init__()

    def setup(self):  # pragma: no cover
        super(DeviceMapping, self).setup(heartbeat_ping=settings.DEVICE_MAPPING_PING)
        self.model = Device(self.conn)

    """
    Find Devices in SQL and add them to ElasticSearch
    """

    def add_devices(self, start_date):
        count = 0
        start = self.max_id() + 1
        logger.debug("Get Devices from {0} to {1} since {2}"
              .format(start, start+self.step_size, start_date))
        for device in self.model.get_devices(start, self.step_size, start_date):
            count += 1

            _action = super(DeviceMapping, self).get_site_values(device.get('ServiceArea'))

            for pfik, pfiv in self.dates_from_pacific:
                _action[pfiv] = convert_pacific_to_utc(device.record[pfik])
                del device.record[pfik]

            if 'TimeZone' in _action:
                for pfik, pfiv in self.dates_to_localize:
                    _action[pfiv] = convert_utc_to_local_time(_action[pfik], _action['TimeZone'])

            device.update(_action)

            rec = device.es()
            logger.debug("Record found: {0}".format(device.get('ID')))
            self.add(rec, self.step_size)

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))

        # only wait between DB calls when there is no delay from ES (HTTP requests)
        if count <= 0:
            self.model.conn.reset()
            logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
            time.sleep(self.db_wait)

    """
    Loop to continuously find new Devices and add them
    """
    def sync(self, start_date):
        while True:
            self.add_devices(start_date)
