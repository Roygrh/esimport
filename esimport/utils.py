################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import datetime
import decimal
import json
import logging
from datetime import datetime, timezone, date

from dateutil import tz

logger = logging.getLogger(__name__)


def convert_utc_to_local_time(time, tzone):
    if time is None:
        return None

    assert isinstance(time, datetime) and time.tzinfo == timezone.utc, "Time zone is not set to UTC."
    local_datetime = time.astimezone(tz.gettz(tzone))
    return local_datetime.replace(tzinfo=tz.gettz(tzone))


def convert_pacific_to_utc(time):
    if time is None:
        return None

    assert isinstance(time, datetime) and time.tzinfo == tz.gettz(
        'America/Los_Angeles'), "Time zone is not set to America/Los_Angeles."
    utc_datetime = time.astimezone(tz.gettz('UTC'))
    return utc_datetime.replace(tzinfo=tz.gettz('UTC'))


def set_pacific_timezone(time):
    if time is None:
        return None

    assert isinstance(time, datetime), "Object is not a datetime object."
    return time.replace(tzinfo=tz.gettz('America/Los_Angeles'))


def set_utc_timezone(time):
    if time is None:
        return None

    assert isinstance(time, datetime), "Object is not a datetime object."
    return time.replace(tzinfo=timezone.utc)


def date_to_index_name(time):
    return time.strftime('%Y-%m')

class ESDataEncoder(json.JSONEncoder):
    # https://gist.github.com/drmalex07/5149635e6ab807c8b21e
    # https://github.com/PyCQA/pylint/issues/414
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            # Property has price field as Decimal and Decimal is not JSON serializable
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def esimport_json_dumps(input_obj:dict):
    return json.dumps(input_obj, cls=ESDataEncoder, separators=(',', ':'))
