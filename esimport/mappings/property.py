import sys
import time
import pprint
import logging
import traceback

from elasticsearch import helpers
from elasticsearch import exceptions
from elasticsearch import Elasticsearch

from esimport import settings
from esimport.models.property import Property
from esimport.connectors.mssql import MsSQLConnector


logger = logging.getLogger(__name__)


class PropertyMapping:

    model = None
    es = None

    _items = None


    def __init__(self):
        self._items = list()
        self.step_size = settings.ES_BULK_LIMIT
        self.pp = pprint.PrettyPrinter(indent=2, depth=10) # pragma: no cover


    def setup(self):
        logger.debug("Setting up DB connection")
        conn = MsSQLConnector()
        self.model = Property(conn)

        logger.debug("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)


    # FIXME: apply extract pull up refactoring
    # duplicate code from esimport/mappings/account.py
    def max_id(self):
        logger.debug("Finding max id from index: %s, type: %s" % (
                    settings.ES_INDEX, self.model.get_type()))
        filters = dict(index=settings.ES_INDEX, doc_type=self.model.get_type(),
                        body={
                            "aggs": {
                                "max_id": {
                                  "max": {
                                    "field": "ID"
                                  }
                                }
                              },
                              "size": 0
                            })
        response = self.es.search(**filters)
        try:
            _id = response['aggregations']['max_id']['value']
            if _id:
                return int(_id)
        except Exception as err:
            logger.error(err)
            traceback.print_exc(file=sys.stdout)
        return 0


    # FIXME: apply extract pull up refactoring
    # duplicate code from esimport/mappings/account.py
    def bulk_add(self, es, actions, retries=settings.ES_RETRIES, timeout=settings.ES_TIMEOUT):
        attempts = 0
        while attempts < retries:
            try:
                attempts += 1
                helpers.bulk(es, actions, request_timeout=timeout)
                break
            except exceptions.ConnectionTimeout as err:
                logger.error(err)
                traceback.print_exc(file=sys.stdout)
                time.sleep(attempts * 5) # pragma: no cover
            except Exception as err:
                logger.error(err)
                traceback.print_exc(file=sys.stdout)
        return attempts


    _items = []
    def add(self, item, limit):
        self._items.append(item)
        items_count = len(self._items)
        if items_count >= limit:
            logger.info("Adding {0} records".format(items_count))
            self.bulk_add(self.es, self._items)
            self._items = []


    def sync(self):
        while True:
            try:
                start = self.max_id()
                for properte in self.model.get_properties(start, self.step_size):
                    logger.debug("Record found: {0}".format(self.pp.pformat(properte.es())))
                    self.add(dict(properte.es()), self.step_size)
            except KeyboardInterrupt:
                pass


    def update(self):
        pass
