################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import logging
import time
from datetime import datetime, timezone

import six
from dateutil import tz
from dateutil.parser import parse

from extensions import sentry_client

logger = logging.getLogger(__name__)

def six_u(v):
    if isinstance(v, six.string_types):
        if six.PY2 and isinstance(v, unicode):
            return v
        return six.u(v)
    else:
        return v

def convert_keys_to_string(dictionary):
    if not isinstance(dictionary, dict):
        return six_u(dictionary)
    return dict((six_u(k), convert_keys_to_string(v))
        for k, v in dictionary.items())

def retry(retry, retry_wait, retry_incremental=True, retry_exception=Exception):
    def tryIt(func):
        def f(*args, **kwargs):
            retries = retry
            retries_wait = retry_wait
            while True:
                try:
                    return func(*args, **kwargs)
                except retry_exception as err:
                    logger.error(err)
                    sentry_client.captureException()
                    if retries > 0:
                        retries -= 1
                        logger.info('Retry {0} of {1} in {2} seconds'
                              .format((retry - retries), retry, retries_wait))
                        time.sleep(retries_wait)
                        if retry_incremental:
                            retries_wait += retry_wait
                    else:
                        sentry_client.captureException()
                        raise err
        return f
    return tryIt

def convert_utc_to_local_time(time, tzone):
    assert isinstance(time, datetime) and time.tzinfo == timezone.utc, "Time zone is not set to UTC."
    local_datetime = time.astimezone(tz.gettz(tzone))
    return local_datetime.replace(tzinfo=tz.gettz(tzone))

def convert_pacific_to_utc(time):
    assert isinstance(time, datetime) and time.tzinfo == tz.gettz('America/Los_Angeles'), "Time zone is not set to America/Los_Angeles."
    utc_datetime = time.astimezone(tz.gettz('UTC'))
    return utc_datetime.replace(tzinfo=tz.gettz('UTC'))

def set_pacific_timezone(time):
    assert isinstance(time, datetime), "Object is not a datetime object."
    return time.replace(tzinfo=tz.gettz('America/Los_Angeles'))

def set_utc_timezone(time):
    assert isinstance(time, datetime), "Object is not a datetime object."
    return time.replace(tzinfo=timezone.utc)
