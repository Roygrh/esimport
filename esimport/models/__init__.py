import logging

from esimport import settings
from esimport import utils

logger = logging.getLogger(__name__)


class ESRecord:

    record = None

    meta_fields = {
        "_op_type": "update",
        "_index": settings.ES_INDEX
    }


    def __init__(self, record, doc_type):
        self.record = record
        self.doc_type = doc_type


    def es(self, record_id=None):
        rec = self.meta_fields.copy()
        rec.update({
            "_type": self.doc_type,
            "_id": record_id or self.record.get('ID'),
            "doc_as_upsert": True,
            "doc": self.record
        })
        rec = utils.convert_keys_to_string(rec)
        return rec


    def get(self, name):
        return self.record.get(name)
