import time
import logging

from elasticsearch import Elasticsearch

from esimport import settings
from esimport.utils import convert_utc_to_local_time
from esimport.models.session import Session
from esimport.mappings.document import DocumentMapping
from esimport.mappings.property import PropertyMapping

logger = logging.getLogger(__name__)

'''
Session mapping is very much like Account mapping
'''


class SessionMapping(DocumentMapping):
    def __init__(self):
        super(SessionMapping, self).__init__()

    def setup(self):  # pragma: no cover
        DocumentMapping.setup(self)
        self.model = Session(self.conn)

    """
    Find Sessions in SQL and add them to ElasticSearch
    """
    def add_sessions(self, start_date):
        count = 0
        start = self.max_id() + 1
        logger.debug("Get Sessions from {0} to {1} since {2}"
              .format(start, start+self.step_size, start_date))
        for session in self.model.get_sessions(start, self.step_size, start_date):
            count += 1

            # get some properties from PropertyMapping
            _action = {}
            for properte in self.pm.get_properties_by_service_area(session.get('ServiceArea')):
                for pfik, pfiv in self.property_fields_include:
                    _action[pfik] = properte.get(pfiv or pfik, "")
                break

            if 'TimeZone' in _action:
                _action['LoginTimeLocal'] = convert_utc_to_local_time(session.record['LoginTime'],
                                                                      _action['TimeZone'])
                _action['LogoutTimeLocal'] = convert_utc_to_local_time(session.record['LogoutTime'],
                                                                       _action['TimeZone'])
            session.update(_action)

            rec = session.es()
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
    Loop to continuously find new Sessions and add them
    """
    def sync(self, start_date):
        while True:
            self.add_sessions(start_date)


    """
    NON FUNCTIONAL. Needs to be implemented.
    """
    def backload(self, start_date):
        start = 0
        for session in self.model.get_sessions(start, self.step_size, start_date):
            rec = session.es()
            logger.debug("Record found: {0}".format(self.pp.pformat(rec)))
            self.add(dict(rec), self.step_size)
            start = session.get('ID') + 1

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))
