import redis
import ast
import logging

from esimport import settings


logger = logging.getLogger(__name__)


class RedisClient(object):
    def __init__(self):
        self.client = redis.Redis(host=settings.REDIS_HOST, 
                                  port=settings.REDIS_PORT)

    def set(self, record):
        for service_area in record['ServiceAreas']:
            service_areas_cache = self.client.lrange(service_area, 0, -1)
                for sa in service_areas_cache:
                    record_cache = ast.literal_eval(sa)
            self.client.rpush(service_area, str(record))    
            logger.debug('Service area: {}'.format(service_area)  )
        
