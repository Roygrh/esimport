import json
from datetime import datetime
from decimal import Decimal

import pytest
import redis
from dateutil import tz

from esimport import settings
from esimport.cache import CacheClient
from esimport.utils import ESDataEncoder


@pytest.fixture()
def clear_redis():
    client = redis.StrictRedis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, encoding="utf-8"
    )
    client.flushdb()
    yield
    client.flushdb()


class TestCacheClient:
    @pytest.mark.usefixtures("clear_redis")
    def test_cache_client(self):
        cc = CacheClient()

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
        encoded_obj = json.dumps(input_obj, cls=ESDataEncoder)
        expected = '{"a": 1.23, "b": "2019-01-01T00:00:00+09:00", "c": 1}'

        assert expected == encoded_obj
