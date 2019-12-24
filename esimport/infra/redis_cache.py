import datetime
import json
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Union

import orjson
import redis

from ._base import BaseInfra


@dataclass
class CacheClient(BaseInfra):

    redis_host: str = "localhost"
    redis_port: int = 6379
    logger: logging.Logger = None

    # Default "time to live" value for the inserted objects
    ttl_value: datetime.timedelta = datetime.timedelta(days=1)

    def __post_init__(self):
        self._log("Setting up cache client")
        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            encoding="utf-8",
            health_check_interval=3,
        )

    def exists(self, key: str) -> bool:
        return self.client.exists(key)

    def get(self, key: str) -> Union[dict, List[dict], None]:
        self._log(f"Cache - getting value for key: {key}", level=logging.DEBUG)
        rec = self.client.get(key)
        return json.loads(rec) if rec else None

    def set(self, key: str, value):
        self._log(f"Cache - setting value for key: {key}", level=logging.DEBUG)
        self.client.setex(key, self.ttl_value, self.orjson_dumps(value))

    # We are going to use orjson (see below), this function is a small wrapper
    # to match the standard json.dumps behavior.
    def orjson_dumps(self, v):
        def default(obj):
            if isinstance(obj, Decimal):
                return str(obj)

        # orjson.dumps returns bytes, to match standard json.dumps we need to call `.decode()`
        return orjson.dumps(v, default=default)  # .decode()
