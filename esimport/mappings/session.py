import time
import logging

from elasticsearch import Elasticsearch

from esimport import settings
from esimport.models.session import Session
from esimport.connectors.mssql import MsSQLConnector
from esimport.mappings.account import AccountMapping
from esimport.mappings.property import PropertyMapping


logger = logging.getLogger(__name__)


'''
Session mapping is very much like Account mapping
'''
class SessionMapping(AccountMapping):


    def __init__(self):
        super(SessionMapping, self).__init__()


    def setup(self): # pragma: no cover
        logger.debug("Setting up DB connection")
        conn = MsSQLConnector()
        self.model = Session(conn)

        # ARRET! possible cycle calls in future
        self.pm = PropertyMapping()
        self.pm.setup()

        logger.debug("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)


    def sync(self, start_date='1900-01-01'):
        while True:
            count = 0
            start = self.max_id() + 1
            for session in self.model.get_sessions(start, self.step_size, start_date):
                count += 1

                # get some properties from PropertyMapping
                _action = {}
                for properte in self.pm.get_properties_by_service_area(session.get('ServiceArea')):
                    for pfik, pfiv in self.property_fields_include:
                        _action[pfik] = properte.get(pfiv or pfik, "")
                    break
                session.update(_action)

                rec = session.es()
                logger.debug("Record found: {0}".format(self.pp.pformat(rec)))
                self.add(rec, self.step_size)

            # for cases when all/remaining items count were less than limit
            self.add(None, min(len(self._items), self.step_size))

            # only wait between DB calls when there is no delay from ES (HTTP requests)
            if count <= 0:
                logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
                time.sleep(self.db_wait)


    def backload(self, start_date):
        start = 0
        for session in self.model.get_sessions(start, self.step_size, start_date):
            rec = session.es()
            logger.debug("Record found: {0}".format(self.pp.pformat(rec)))
            self.add(dict(rec), self.step_size)
            start = session.get('ID') + 1

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))
