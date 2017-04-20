import sys
import time
import logging
import traceback

from elasticsearch import helpers
from elasticsearch import exceptions

from esimport import settings


logger = logging.getLogger(__name__)


class BaseMapping(object):


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


    def bulk_add_or_update(self, es, actions, retries=settings.ES_RETRIES, timeout=settings.ES_TIMEOUT):
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


    def get_es_count(self):
        logger.debug("Finding records count from index: %s, type: %s" % (
                    settings.ES_INDEX, self.model.get_type()))
        filters = dict(index=settings.ES_INDEX, doc_type=self.model.get_type())
        response = self.es.count(**filters)
        try:
            return response['count']
        except Exception as err:
            logger.error(err)
            traceback.print_exc(file=sys.stdout)
        return 0
