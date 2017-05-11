import six
import time

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
                    if retries > 0:
                        retries -= 1
                        logger.info('Retry {0} of {1} in {2} seconds'
                              .format((retry - retries), retry, retries_wait))
                        time.sleep(retries_wait)
                        if retry_incremental:
                            retries_wait += retry_wait
                    else:
                        raise err
        return f
    return tryIt
