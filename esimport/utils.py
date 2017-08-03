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

