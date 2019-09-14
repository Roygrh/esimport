import redis
import json
import logging
import datetime

from esimport import settings
from esimport.utils import ESDataEncoder

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


