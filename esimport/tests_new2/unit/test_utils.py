from datetime import datetime
from datetime import timezone

import pytest
from dateutil import tz

from esimport.utils import convert_pacific_to_utc
from esimport.utils import convert_utc_to_local_time
from esimport.utils import date_to_index_name
from esimport.utils import set_pacific_timezone
from esimport.utils import set_utc_timezone


class TestUtils:
    def test_convert_utc_to_local_time(self):
        assert convert_utc_to_local_time(None, None) is None

        with pytest.raises(AssertionError) as execption_info:
            input_time = datetime(2019, 1, 1, 13, 11, 12)
            convert_utc_to_local_time(input_time, "Asia/Tokyo")

        assert execption_info.match("Time zone is not set to UTC.")

        input_time = datetime(2019, 1, 1, 13, 11, 12, tzinfo=timezone.utc)
        result = convert_utc_to_local_time(input_time, "Asia/Tokyo")  # UTC+9
        expected = datetime(2019, 1, 1, 22, 11, 12, tzinfo=tz.gettz("Asia/Tokyo"))
        assert result == expected

    def test_convert_pacific_to_utc(self):

        assert convert_pacific_to_utc(None) is None

        with pytest.raises(AssertionError) as execption_info:
            input_time = datetime(2019, 1, 1, 13, 11, 12, tzinfo=timezone.utc)
            convert_pacific_to_utc(input_time)

        assert execption_info.match("Time zone is not set to America/Los_Angeles.")

        input_time = datetime(
            2019, 1, 1, 13, 11, 12, tzinfo=tz.gettz("America/Los_Angeles")
        )
        result = convert_pacific_to_utc(input_time)
        expected = datetime(2019, 1, 1, 21, 11, 12, tzinfo=timezone.utc)
        assert result == expected

    def test_set_pacific_timezone(self):

        assert set_pacific_timezone(None) is None

        input_time = datetime(2019, 1, 1, 13, 11, 12, tzinfo=timezone.utc)
        result = set_pacific_timezone(input_time)
        expect = datetime(
            2019, 1, 1, 13, 11, 12, tzinfo=tz.gettz("America/Los_Angeles")
        )
        assert result == expect

    def test_set_utc_timezone(self):

        assert set_utc_timezone(None) is None

        input_time = datetime(
            2019, 1, 1, 13, 11, 12, tzinfo=tz.gettz("America/Los_Angeles")
        )
        expect = datetime(2019, 1, 1, 13, 11, 12, tzinfo=timezone.utc)
        result = set_utc_timezone(input_time)
        assert result == expect

    def test_date_to_index_name(self):
        input_time = datetime(2019, 1, 1)
        result = date_to_index_name(input_time)
        expect = "2019-01"
        assert result == expect
