import redis

from esimport import settings


class RedisClient(object):
    def __init__(self):
        self.client = redis.Redis(host=settings.REDIS_HOST, 
                                  port=settings.REDIS_PORT)

    def set(self, key, value):
        pass    
