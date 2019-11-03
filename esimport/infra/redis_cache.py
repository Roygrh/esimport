import datetime
import json
import logging
from dataclasses import dataclass
from typing import Union, List
import redis

from esimport.utils import esimport_json_dumps

from ._base import BaseInfra


@dataclass
class CacheClient(BaseInfra):

    redis_host: str = "localhost"
    redis_port: int = 6379

    # Default "time to live" value for the inserted objects
    ttl_value: datetime.timedelta = datetime.timedelta(days=1)

    def __post_init__(self):
        self._log("Setting up cache client")
        self.client = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, encoding="utf-8"
        )

    def exists(self, key: str) -> bool:
        return self.client.exists(key)

    def get(self, key: str) -> Union[dict, List[dict], None]:
        self._log(f"Cache - getting value for key: {key}", level=logging.DEBUG)
        rec = self.client.get(key)
        return json.loads(rec) if rec else None

    def set(self, key: str, value):
        self._log(f"Cache - setting value for key: {key}", level=logging.DEBUG)
        self.client.setex(key, self.ttl_value, esimport_json_dumps(value))
