import time
import logging

from esimport.utils import convert_utc_to_local_time, convert_pacific_to_utc
from esimport.models.conference import Conference
from esimport.mappings.document import DocumentMapping

logger = logging.getLogger(__name__)


class ConferenceMapping(DocumentMapping):
    def __init__(self):
        super(ConferenceMapping, self).__init__()

    def setup(self):  # pragma: no cover
        DocumentMapping.setup(self)
        self.model = Conference(self.conn)

    """
    Find Conference in SQL and add them to ElasticSearch
    """
    def add_conferences(self, start_date):
        count = 0
        start = self.max_id() + 1
        logger.debug("Get Conferences from {0} to {1} since {2}"
              .format(start, start+self.step_size, start_date))
        for conference in self.model.get_conferences(start, self.step_size, start_date):
            count += 1

            # get some properties from PropertyMapping
            _action = {}
            for properte in self.pm.get_properties_by_service_area(conference.get('ServiceArea')):
                for pfik, pfiv in self.property_fields_include:
                    _action[pfik] = properte.get(pfiv or pfik, "")
                break

            if 'TimeZone' in _action:
                _action['DateCreatedLocal'] = convert_utc_to_local_time(conference.record['DateCreatedUTC'],
                                                                       _action['TimeZone'])
                _action['StartDateLocal'] = convert_utc_to_local_time(conference.record['StartDateUTC'], _action['TimeZone'])
                _action['EndDateLocal'] = convert_utc_to_local_time(conference.record['EndDateUTC'],
                                                                      _action['TimeZone'])
            conference.update(_action)

            rec = conference.es()
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
            self.add_conferences(start_date)

    """
    Continuously update ElasticSearch to have the latest Conference data
    """
    def update(self, start_date):
        start = 0
        while True:
            count = 0
            for conf in self.model.get_conferences(start, self.step_size, start_date):
                count += 1
                logger.debug("Record found: {0}".format(self.pp.pformat(conf.es())))

                # get some properties from PropertyMapping
                _action = {}
                for properte in self.pm.get_properties_by_service_area(conf.get('ServiceArea')):
                    for pfik, pfiv in self.property_fields_include:
                        _action[pfik] = properte.get(pfiv or pfik, "")
                    break

                if 'TimeZone' in _action:
                    _action['DateCreatedLocal'] = convert_utc_to_local_time(conf.record['DateCreatedUTC'],
                                                                            _action['TimeZone'])
                    _action['StartDateLocal'] = convert_utc_to_local_time(conf.record['StartDateUTC'],
                                                                          _action['TimeZone'])
                    _action['EndDateLocal'] = convert_utc_to_local_time(conf.record['EndDateUTC'],
                                                                        _action['TimeZone'])

                conf.update(_action)
                self.add(dict(conf.es()), self.step_size)
                start = conf.record.get('ID')

            # for cases when all/remaining items count were less than limit
            self.add(None, min(len(self._items), self.step_size))
            #start += count

            # always wait between DB calls
            time.sleep(self.db_wait)

            if count <= 0:
                start = 0
                time.sleep(self.db_wait * 4)
