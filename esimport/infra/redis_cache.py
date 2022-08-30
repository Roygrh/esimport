import datetime
import json
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Union
import orjson
import redis
import time
from ._base import BaseInfra


def retry_on_connection_refused(func):
    def wrapper(self, *args, **kwargs):
        retries = getattr(self, "redis_retries_on_conn_failure")
        log = getattr(self, "_log")

        for iteration in range(1, retries + 1):
            try:
                return func(self, *args, **kwargs)
            except redis.exceptions.ConnectionError:
                if iteration == retries:
                    raise

                log(f"Got Redis connection error, retrying... {iteration}")
                time.sleep(iteration)

    return wrapper


@dataclass
class CacheClient(BaseInfra):

    redis_host: str = "localhost"
    redis_port: int = 6379
    logger: logging.Logger = None

    # Default "time to live" value for the inserted objects
    ttl_value: datetime.timedelta = datetime.timedelta(days=1)

    # sometimes, too many requests at the same time to Redis by other instances of
    # esimport causes Redis connection refused error. This attribute defines how many
    # times we need to retry before giving up when a connection error happens.
    redis_retries_on_conn_failure = 3

    def __post_init__(self):
        self._log("Setting up cache client")
        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            encoding="utf-8",
            health_check_interval=3,
        )

    @retry_on_connection_refused
    def exists(self, key: str) -> bool:
        if key is None:
            return False
        # exists may return 0, lets make it True or False
        return False if not self.client.exists(key) else True

    @retry_on_connection_refused
    def get(self, key: str) -> Union[dict, List[dict], None]:
        self._log(f"Cache - getting value for key: {key}", level=logging.DEBUG)
        rec = self.client.get(key)
        return json.loads(rec) if rec else None

    @retry_on_connection_refused
    def raw_get(self, key: str) -> Union[str, None]:
        self._log(f"Cache - getting value for key: {key}", level=logging.DEBUG)
        cached_value = self.client.get(key)
        return cached_value.decode("utf-8") if isinstance(cached_value, bytes) else cached_value

    @retry_on_connection_refused
    def set(self, key: str, value):
        self._log(f"Cache - setting value for key: {key}", level=logging.DEBUG)
        self.client.setex(key, self.ttl_value, self.orjson_dumps(value))

    @retry_on_connection_refused
    def raw_setex(self, key: str, value: str, ttl: datetime.timedelta):
        self._log(
            f"Cache - {key} for {ttl.total_seconds()} seconds", level=logging.DEBUG
        )
        self.client.setex(key, ttl, value)

    # We are going to use orjson (see below), this function is a small wrapper
    # to match the standard json.dumps behavior.
    def orjson_dumps(self, v):
        def default(obj):
            if isinstance(obj, Decimal):
                return str(obj)

        # orjson.dumps returns bytes, to match standard json.dumps we need to call `.decode()`
        return orjson.dumps(v, default=default)  # .decode()
