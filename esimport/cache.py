import redis
import ast
import logging
import datetime

from esimport import settings


logger = logging.getLogger(__name__)


class RedisClient(object):
    def __init__(self):
        self.client = redis.StrictRedis(host=settings.REDIS_HOST, 
                                        port=settings.REDIS_PORT,
                                        encoding='utf-8')

    def set(self, record):
        # convert datetime objects to isoformat
        for k, v in record.items():
            if isinstance(v, datetime.datetime):
                record[k] = v.isoformat()
        for service_area in record['ServiceAreas']:
            self.client.set('{0}:{1}'.format(service_area, record['ID']), str(record))
            logger.debug("ID added to set: 'record:{}'".format(record['ID']))
        
