import time
import pprint
import logging

from elasticsearch import Elasticsearch
from elasticsearch import exceptions

from esimport.utils import retry
from esimport import settings
from esimport.models.property import Property
from esimport.connectors.mssql import MsSQLConnector
from esimport.mappings.base import BaseMapping


logger = logging.getLogger(__name__)


class PropertyMapping(BaseMapping):

    model = None
    es = None


    def __init__(self):
        super(PropertyMapping, self).__init__()
        self.step_size = settings.ES_BULK_LIMIT
        self.pp = pprint.PrettyPrinter(indent=2, depth=10) # pragma: no cover


    def setup(self):
        logger.debug("Setting up DB connection")
        conn = MsSQLConnector()
        self.model = Property(conn)

        logger.debug("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)


    def sync(self):
        while True:
            count = 0
            start = self.max_id()
            for properte in self.model.get_properties(start, self.step_size):
                count += 1
                logger.debug("Record found: {0}".format(self.pp.pformat(properte.es())))
                self.add(dict(properte.es()), self.step_size)

            # for cases when all/remaining items count were less than limit
            self.add(None, min(len(self._items), self.step_size))

            # only wait between DB calls when there is no delay from ES (HTTP requests)
            if count <= 0:
                logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
                time.sleep(self.db_wait)


    def get_existing_properties(self, start, limit):
        logger.debug("Fetching {0} records from ES where ID >= {1}" \
                .format(limit, start))
        records = self.es.search(index=settings.ES_INDEX, doc_type=Property.get_type(),
                                 sort="ID:asc", size=limit,
                                 q="ID:[{0} TO *]".format(start))
        for record in records['hits']['hits']:
            yield record.get('_source')


    def update(self):
        start = 0
        while True:
            count = 0
            total = self.get_es_count()
            for properte in self.get_existing_properties(start, self.step_size):
                count += 1

            start += min(self.step_size, total-start)
            if start >= total:
                start = 0

            # only wait between DB calls when there is no delay from ES (HTTP requests)
            if count <= 0:
                logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
                time.sleep(self.db_wait)


    @retry(settings.ES_RETRIES, settings.ES_RETRIES_WAIT, retry_exception=exceptions.ConnectionError)
    @retry(settings.ES_RETRIES, settings.ES_RETRIES_WAIT, retry_exception=exceptions.ConnectionTimeout)
    def get_properties_by_service_area(self, service_area):
        logger.debug("Fetching records from ES where field name {0} exists." \
                .format(service_area))
        records = self.es.search(index=settings.ES_INDEX, doc_type=Property.get_type(),
                                 body={
                                    "query": {
                                        "exists": {
                                            "field" : service_area
                                        }
                                    }
                                 })
        for record in records['hits']['hits']:
            yield record.get('_source')
