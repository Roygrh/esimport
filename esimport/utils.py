################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import six
import time

from extensions import sentry_client

from datetime import datetime
from dateutil import tz

import logging
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
            while True:
                print("EXCEPTION")
                print(retry_exception)
                try:
                    return func(*args, **kwargs)
                except retry_exception as err:
                    logger.error(err)
                    sentry_client.captureException()
                    logger.info('Retry in {0} seconds'.format(retry_wait))
                    time.sleep(retry_wait)
        return f
    return tryIt


def convert_utc_to_local_time(time, timezone):
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
        try:
            time_dt = datetime.strptime(time, fmt).replace(tzinfo=tz.gettz('UTC'))
            local = time_dt.astimezone(tz.gettz(timezone))
            return local.replace(tzinfo=None).isoformat()
        except ValueError:
            pass
        except TypeError:
            return
    return

def convert_pacific_to_utc(time):
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
        try:
            time_dt = datetime.strptime(time, fmt).replace(tzinfo=tz.gettz('PST8PDT'))
            utc = time_dt.astimezone(tz.gettz('UTC'))
            return utc.replace(tzinfo=None).isoformat()
        except ValueError:
            pass
        except TypeError:
            return
    return

