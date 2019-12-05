import json
from datetime import datetime
from decimal import Decimal

from dateutil import tz

from esimport.infra import CacheClient


class TestCacheClient:
    def test_cache_client(self):
        cc = CacheClient()
        cc.client.flushdb()
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
