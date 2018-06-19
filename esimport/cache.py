import redis
import json
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
        datetime_fields = ['CreatedUTC', 'GoLiveUTC']
        for dt in datetime_fields:
            if record.get(dt):
                record[dt] = record[dt].isoformat()
        for service_area in record['ServiceAreas']:
            self.client.set('{0}:{1}'.format(service_area, record['ID']), json.dumps(record))
            logger.debug("ID added to set: 'record:{}'".format(record['ID']))
        
    def get_keys(self, service_area):
        service_area_keys = self.client.keys(pattern='*{}*'.format(service_area))
        return service_area_keys

    def get_record_by_key(self, key):
        rec = self.client.get(key)
        d = json.loads(rec)
        return d
