from datetime import datetime

from esimport_retention_core import filter_old_indices
from esimport_retention_core import gen_indices_wildcard
from esimport_retention_core import gen_previous_month_indices_name
from esimport_retention_core import get_last_retention_month
from esimport_retention_core import get_previous_month_str
from esimport_retention_core import parse_es_url
from esimport_retention_core import parse_es_urls


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
            "a-b-c-2018-10",
            "a-b-c-2018-11",
            "a-b-c-2018-12",
            "a-b-c-2019-01",
            "a-b-c-2019-02",
            "a-b-c-2019-03",
            "a-b-c-2019-04",
            "a-b-c-2019-05",
        ]

        result = [
            x
            for x in filter(
                lambda x: filter_old_indices(x, datetime(2019, 4, 1)), input_indices
            )
        ]
        expected = [
            "a-b-c-2018-10",
            "a-b-c-2018-11",
            "a-b-c-2018-12",
            "a-b-c-2019-01",
            "a-b-c-2019-02",
            "a-b-c-2019-03",
            "a-b-c-2019-04",
        ]
        assert sorted(result) == sorted(expected)

        result = [
            x
            for x in filter(
                lambda x: filter_old_indices(x, datetime(2018, 11, 1)), input_indices
            )
        ]
        expected = ["a-b-c-2018-10", "a-b-c-2018-11"]
        assert sorted(result) == sorted(expected)

        input_indices = [
            "a-b-c-2018-01",
            "a-b-c-2018-02",
            "a-b-c-2018-03",
            "a-b-c-2018-04",
            "a-b-c-2018-05",
            "a-b-c-2018-06",
            "a-b-c-2018-07",
            "a-b-c-2018-08",
            "a-b-c-2018-09",
            "a-b-c-2018-10",
            "a-b-c-2018-11",
            "a-b-c-2018-12",
            "a-b-c-2019-01",
            "a-b-c-2019-02",
            "a-b-c-2019-03",
            "a-b-c-2019-04",
            "a-b-c-2019-05",
            "a-b-c-2019-06",
            "a-b-c-2019-07",
            "a-b-c-2019-08",
            "a-b-c-2019-09",
            "a-b-c-2019-10",
            "a-b-c-2019-11",
            "a-b-c-2019-12",
        ]

        cur_date = datetime(2019, 12, 15)
        retention_policy = 18
        result = [
            x
            for x in filter(
                lambda x: filter_old_indices(
                    x, get_last_retention_month(cur_date, retention_policy)
                ),
                input_indices,
            )
        ]
        expected = [
            "a-b-c-2018-01",
            "a-b-c-2018-02",
            "a-b-c-2018-03",
            "a-b-c-2018-04",
            "a-b-c-2018-05",
            "a-b-c-2018-06",
        ]
        assert sorted(result) == sorted(expected)

        cur_date = datetime(2019, 12, 15)
        retention_policy = 24

        result = [
            x
            for x in filter(
                lambda x: filter_old_indices(
                    x, get_last_retention_month(cur_date, retention_policy)
                ),
                input_indices,
            )
        ]
        expected = []
        assert sorted(result) == sorted(expected)

        cur_date = datetime(2018, 2, 15)
        retention_policy = 1

        result = [
            x
            for x in filter(
                lambda x: filter_old_indices(
                    x, get_last_retention_month(cur_date, retention_policy)
                ),
                input_indices,
            )
        ]
        expected = ["a-b-c-2018-01"]
        assert sorted(result) == sorted(expected)

        cur_date = datetime(2018, 1, 15)
        retention_policy = 1

        result = [
            x
            for x in filter(
                lambda x: filter_old_indices(
                    x, get_last_retention_month(cur_date, retention_policy)
                ),
                input_indices,
            )
        ]
        expected = []
        assert sorted(result) == sorted(expected)

    def test_get_previous_month_str(self):
        input_date = datetime(2019, 1, 1)
        expected_str = "2018-12"
        result = get_previous_month_str(input_date)
        assert expected_str == result


class TestIndiciesNames:
    def test_gen_indices_wildcard(self):
        input_str = "a , b, c       "
        expect = ["a-*", "b-*", "c-*"]
        result = gen_indices_wildcard(input_str)
        assert expect == result

        input_str = "  "
        expect = []
        result = gen_indices_wildcard(input_str)
        assert expect == result

    def test_gen_previous_month_indices_name(self):
        input_str = "a,b,c"
        input_date = datetime(2019, 1, 1)
        result = gen_previous_month_indices_name(input_str, input_date)
        expected = ["a-2018-12", "b-2018-12", "c-2018-12"]
        assert result == expected


class TestUrlParser:
    def test_parse_es_url(self):
        input_url = "https://search-sample-domain-00000000000000000000000001.us-west-2.es.amazonaws.com/"
        result = parse_es_url(input_url)
        expected = (
            "us-west-2",
            "search-sample-domain-00000000000000000000000001.us-west-2.es.amazonaws.com",
        )
        assert result == expected

    def test_parse_es_urls(self):
        input_urls = (
            "https://search-sample-domain-00000000000000000000000001.us-west-1.es.amazonaws.com/,"
            "https://search-sample-domain-00000000000000000000000002.us-west-2.es.amazonaws.com/,"
            "https://search-sample-domain-00000000000000000000000003.us-east-1.es.amazonaws.com/,"
            "https://search-sample-domain-00000000000000000000000004.us-east-2.es.amazonaws.com/,"
        )

        result = sorted(parse_es_urls(input_urls), key=lambda x: x[0])
        expected = sorted(
            [
                (
                    "us-west-1",
                    "search-sample-domain-00000000000000000000000001.us-west-1.es.amazonaws.com",
                ),
                (
                    "us-west-2",
                    "search-sample-domain-00000000000000000000000002.us-west-2.es.amazonaws.com",
                ),
                (
                    "us-east-1",
                    "search-sample-domain-00000000000000000000000003.us-east-1.es.amazonaws.com",
                ),
                (
                    "us-east-2",
                    "search-sample-domain-00000000000000000000000004.us-east-2.es.amazonaws.com",
                ),
            ],
            key=lambda x: x[0],
        )

        assert result == expected
