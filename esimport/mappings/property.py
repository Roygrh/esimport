import sys
import logging
import traceback

from esimport import settings
from esimport.models import Property
from esimpot.mappings import Mapping


logger = logging.getLogger(__name__)


class PropertyMapping(Mapping):

    doc_type = Property.get_type()

    # FIXME: apply extract pull up refactoring
    # duplicate code from esimport/mappings/account.py
    def max_id(self):
        logger.debug("Finding max id from index: %s, type: %s" % (
                    settings.ES_INDEX, self.doc_type))
        filters = dict(index=settings.ES_INDEX, doc_type=self.doc_type,
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


    def sync(self):
        pass


    def update(self):
        pass
