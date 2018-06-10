import redis
import ast
import logging
import datetime
import ast

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
        
    def get_keys(self, service_area):
        service_area_keys = self.client.keys(pattern='*{}*'.format(service_area))
        return service_area_keys

    def get_record_by_key(self, key):
        rec = self.client.get(key).decode('utf-8')
        d = ast.literal_eval(rec)
        return d
