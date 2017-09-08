import time
import logging

from esimport.utils import convert_utc_to_local_time, convert_pacific_to_utc
from esimport.models.device import Device
from esimport.mappings.document import DocumentMapping

logger = logging.getLogger(__name__)


class DeviceMapping(DocumentMapping):
    def __init__(self):
        super(DeviceMapping, self).__init__()

    def setup(self):  # pragma: no cover
        DocumentMapping.setup(self)
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

            # get some properties from PropertyMapping
            _action = {}
            for properte in self.pm.get_properties_by_service_area(device.get('ServiceArea')):
                for pfik, pfiv in self.property_fields_include:
                    _action[pfik] = properte.get(pfiv or pfik, "")
                break

            _action['DateUTC'] = convert_pacific_to_utc(device.record['Date'])
            del device.record['Date']

            if 'TimeZone' in _action:
                _action['DateLocal'] = convert_utc_to_local_time(_action['DateUTC'],
                                                                       _action['TimeZone'])
            device.update(_action)

            rec = device.es()
            logger.debug("Record found: {0}".format(self.pp.pformat(rec)))
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
