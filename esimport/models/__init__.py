import logging

from esimport import settings


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


    def es(self):
        rec = self.meta_fields.copy()
        rec.update({
            "_type": self.doc_type,
            "_id": self.record.get('ID'),
            "doc_as_upsert": True,
            "doc": self.record
        })
        return rec
