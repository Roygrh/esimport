################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import logging
from esimport import settings
from ..utils import date_to_index_name
logger = logging.getLogger(__name__)


class ESRecord:

    record = None

    meta_fields = {
        "_op_type": "update"
    }

    def __init__(self, record, doc_type, index_prefix, index_date=None):
        self.record = record
        self.doc_type = doc_type
        self.index_prefix = index_prefix
        self.index_date = index_date

    def es(self, record_id=None):
        if self.index_date:
            index_name = "{0}-{1}".format(self.index_prefix, date_to_index_name(self.index_date))
        else:
            index_name = self.index_prefix

        rec = self.meta_fields.copy()
        rec.update({
            "_index": index_name,
            "_type": self.doc_type,
            "_id": record_id or self.record.get('ID'),
            "doc_as_upsert": True,
            "doc": self.record
        })
        return rec

    def get(self, name):
        return self.record.get(name)

    def update(self, d):
        return self.record.update(d)
