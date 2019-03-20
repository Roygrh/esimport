import redis
import json
import logging
import datetime
import decimal

from esimport import settings

logger = logging.getLogger(__name__)

class CacheClient(object):
    def __init__(self):
        logger.info("Setting up cache client")
        self.client = redis.StrictRedis(host=settings.REDIS_HOST, 
                                        port=settings.REDIS_PORT,
                                        encoding='utf-8')

    def exists(self, key):
        return self.client.exists(key)

    def get(self, key):
        logger.debug("Cache - getting value for key: {0}".format(key))
        rec = self.client.get(key)
        return json.loads(rec) if rec else None

    def set(self, key, value):
        logger.debug("Cache - setting value for key: {0}".format(key))
        self.client.setex(key, datetime.timedelta(days=1), json.dumps(value, cls=ESDataEncoder))

# https://gist.github.com/drmalex07/5149635e6ab807c8b21e
class ESDataEncoder(json.JSONEncoder):
    # https://github.com/PyCQA/pylint/issues/414
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal): 
            # Property has price field as Decimal and Decimal is not JSON serializable
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)
