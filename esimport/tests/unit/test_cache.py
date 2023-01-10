import json
from datetime import datetime
from decimal import Decimal

import pytest
import redis.exceptions
from dateutil import tz

from esimport.infra import CacheClient
from esimport.core import Config


class TestCacheClient:
    def test_connection(self):
        config = Config()
        cc = CacheClient(redis_host=config.redis_host, redis_port=config.redis_port)
        cc.client.flushdb()
        cc.set("test_key", {"a": 1, "b": 2})
        assert cc.exists("test_key") is True

        # wrong host and port
        with pytest.raises(redis.exceptions.ConnectionError) as exc_info:
            cc = CacheClient(redis_host="localhostt", redis_port=1111)
            cc.set("test_key", {"a": 1, "b": 2})

    def test_cache_client(self):
        config = Config()
        cc = CacheClient(redis_host=config.redis_host, redis_port=config.redis_port)
        cc.client.flushdb()
        assert cc.exists(None) is False
        assert cc.exists("test_key") is False

        cc.set("test_key", {"a": 1, "b": 2})
        assert cc.exists("test_key") is True

        result = cc.get("test_key")
        assert result == {"a": 1, "b": 2}

        assert cc.get("not-existed") is None


class TestESDataEncoder:
    def test_esdata_encoder(self):

        input_obj = {
            "a": Decimal("1.23"),
            "b": datetime(2019, 1, 1, tzinfo=tz.gettz("Asia/Tokyo")),
            "c": 1,
        }
        c = CacheClient()
        encoded_obj = c.orjson_dumps(input_obj)
        expected = c.orjson_dumps(
            {"a": "1.23", "b": "2019-01-01T00:00:00+09:00", "c": 1}
        )
        print(encoded_obj, encoded_obj)
        assert expected == encoded_obj
