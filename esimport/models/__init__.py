################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import logging
from datetime import timezone
from datetime import datetime

from dateutil.parser import parse

from ..utils import date_to_index_name
from typing import Union

logger = logging.getLogger(__name__)


class ESRecord:

    record = None

    meta_fields = {"_op_type": "index"}

    def __init__(self, record: dict, doc_type:str, index_prefix: str, version_date: str, index_date=None):
        self.record = record
        self.doc_type = doc_type
        self.index_prefix = index_prefix
        self.index_date = index_date
        self.version = self.get_version_from_date_field(version_date)

    def es(self, record_id=None):
        if self.index_date:
            index_name = "{0}-{1}".format(
                self.index_prefix, date_to_index_name(self.index_date)
            )
        else:
            index_name = self.index_prefix

        rec = self.meta_fields.copy()
        rec.update(
            {
                "_index": index_name,
                "_type": self.doc_type,
                "_id": record_id or self.record.get("ID"),
                "_version": self.version,
                "_version_type": "external",
                "_source": self.record

            }
        )

        return rec

    def get(self, name):
        return self.record.get(name)

    def update(self, d):
        return self.record.update(d)

    @staticmethod
    def get_version_from_date_field(date_str: str):
        parsed_date = parse(date_str)

        # if datetime object does not have timezone information then `timestamp()` method will treat datetime
        # object as it in local timezone. If OS timezone will not be set to UTC it may lead to unexpected results.
        # It is an edge case, but explicitly configure timezone will give stable results.
        # So if timezone does not parsed then assuming that date belongs to UTC timezone
        if parsed_date.tzinfo is None:
            parsed_date.replace(tzinfo=timezone.utc)

        # need microsecond precision because documents can be changed many times during one second period
        # and for each change we need a new version number
        return int(parsed_date.timestamp() * 1000000)
