from datetime import datetime

from esimport_retention import filter_old_indices
from esimport_retention import gen_indices_wildcard
from esimport_retention import get_last_retention_month


class TestRetentionCalendar:
    def test_get_last_retention_mont(self):
        age = 1
        result = get_last_retention_month(datetime(2019, 3, 1), age)
        expect = datetime(2019, 2, 1)
        assert expect == result

        age = 18
        result = get_last_retention_month(datetime(2019, 3, 1), age)
        expect = datetime(2017, 9, 1)
        assert expect == result

        age = 18
        result = get_last_retention_month(datetime(2019, 12, 1), age)
        expect = datetime(2018, 6, 1)
        assert expect == result

        age = 18
        result = get_last_retention_month(datetime(2016, 2, 29), age)
        expect = datetime(2014, 8, 1)
        assert expect == result

    def test_filter_old_indices(self):
        input_indices = [
            "a-2018-10",
            "a-2018-11",
            "a-2018-12",
            "a-2019-01",
            "a-2019-02",
            "a-2019-03",
            "a-2019-04",
            "a-2019-05",
        ]

        result = [
            x
            for x in filter(
                lambda x: filter_old_indices(x, datetime(2019, 4, 1)), input_indices
            )
        ]
        expected = [
            "a-2018-10",
            "a-2018-11",
            "a-2018-12",
            "a-2019-01",
            "a-2019-02",
            "a-2019-03",
            "a-2019-04",
        ]
        assert result == expected

        result = [
            x
            for x in filter(
                lambda x: filter_old_indices(x, datetime(2018, 11, 1)), input_indices
            )
        ]
        expected = ["a-2018-10", "a-2018-11"]
        assert result == expected


class TestIndiciesWildcards:
    def test_gen_indices_wildcard(self):
        input_str = "a , b, c       "
        expect = ["a-*", "b-*", "c-*"]
        result = gen_indices_wildcard(input_str)
        assert expect == result
