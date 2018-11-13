################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import logging
import time
from datetime import datetime

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


def convert_utc_to_local_time(time, timezone):
    try:
        utc_datetime = parse(time)
    except (ValueError, TypeError):
        return 
    
    # Make sure to consider the received datetime object as UTC
    # before doing that, remove any already-set tzinfo
    utc_datetime = utc_datetime.replace(tzinfo=tz.gettz("UTC"))
    # Do the convertion
    local_datetime = utc_datetime.astimezone(tz.gettz(timezone))
    # Return the new date is ISO 8601 format
    return local_datetime.replace(tzinfo=tz.gettz(timezone)).isoformat()

def convert_pacific_to_utc(time):
    try:
        pacific_datetime = parse(time)
    except (ValueError, TypeError):
        return 
    
    # Make sure to consider the received datetime object as Pacific
    # before doing that, remove any already-set tzinfo
    pacific_datetime = pacific_datetime.replace(tzinfo=tz.gettz('PST8PDT'))
    # Do the convertion
    utc_datetime = pacific_datetime.astimezone(tz.gettz('UTC'))
    # Return the new UTC date is ISO 8601 format
    return utc_datetime.replace(tzinfo=tz.gettz('UTC')).isoformat()
