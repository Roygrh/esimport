import json
from datetime import datetime
from decimal import Decimal

import pytest
from dateutil import tz

from esimport.cache import CacheClient
from esimport.utils import esimport_json_dumps

from esimport.tests_new2.base_fixutres import clear_redis


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
        encoded_obj = esimport_json_dumps(input_obj)
        expected = '{"a": 1.23, "b": "2019-01-01T00:00:00+09:00", "c": 1}'

        assert expected == encoded_obj
