################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
from esimport import settings

# REVIEW: It appears like this is not needed.  Let's remove unused code.
from esimport import utils


import logging
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
        # REVIEW: Let's remove commented out code if it's no longer needed.
        # rec = utils.convert_keys_to_string(rec)
        return rec

    def get(self, name):
        return self.record.get(name)

    def update(self, d):
        return self.record.update(d)
