import csv

from unittest import TestCase
from collections import namedtuple
from datetime import datetime

import testing.elasticsearch
from elasticsearch import Elasticsearch
from mock import Mock, MagicMock

from esimport.models.account import Account
from esimport.mappings.account import AccountMapping
from esimport import settings


class TestAccountMapping(TestCase):

    def _mocked_sql(self):
        dt_format = '%Y-%m-%d %H:%M:%S.%f'

        rows = []
        with open('{0}/multiple_orders.csv'.format(settings.TEST_FIXTURES_DIR)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_tuple = namedtuple('GenericDict', row.keys())(**row)
                row_tuple = row_tuple._replace(Created=datetime.strptime(row_tuple.Created, dt_format))
                row_tuple = row_tuple._replace(Activated=datetime.strptime(row_tuple.Activated, dt_format))
                rows.append(row_tuple)
        return rows


    def setUp(self):
        self.rows = self.multiple_orders = self._mocked_sql()

        self.am = AccountMapping()
        self.am.setup_config()
        self.start = self.am.position
        self.end = self.start + (self.am.step_size * 10)
        self.am.cursor = Mock()
        self.am.cursor.execute = MagicMock(return_value=self.rows)

        # needs ES_HOME set to where elastic search is downloaded
        self.elasticsearch = testing.elasticsearch.Elasticsearch()


    def test_setup_config(self):
        am = AccountMapping()

        assert am.cfg is None
        assert am.step_size is None
        assert am.position is None
        assert am.esTimeout is None
        assert am.esRetry is None

        am.setup_config()

        assert am.cfg is not None
        assert am.step_size is not None
        assert am.position is not None
        assert am.esTimeout is not None
        assert am.esRetry is not None

        am.setup_config()


    # also an integration test
    def test_bulk_add(self):
        es = Elasticsearch(**self.elasticsearch.dsn())

        # Note: start and end inputs are ignored because test data is hard coded
        accounts = self.am.get_accounts(self.start, self.end)
        actions = [account.action for account in accounts]
        self.am.bulk_add(es, actions, self.am.esRetry, self.am.esTimeout)

        _index = Account.get_index()
        _type = Account.get_type()
        for action in actions:
            es_record = es.get(index=_index, doc_type=_type, id=action.get('_id'))
            input_doc = action.get('doc', {})
            saved_doc = es_record.get('_source', {})
            self.assertEqual(input_doc, saved_doc)


    def test_bulk_add_retry(self):
        wrong_dsn = {'hosts': ['127.0.0.1:57288']}
        es = Elasticsearch(**wrong_dsn)

        # Note: start and end inputs are ignored because test data is hard coded
        accounts = self.am.get_accounts(self.start, self.end)
        actions = [account.action for account in accounts]

        attempts = self.am.bulk_add(es, actions, 1, self.am.esTimeout)
        self.assertGreater(attempts, 0)


    # whether returned result count is equal to request count
    def test_get_accounts(self):
        accounts = self.am.get_accounts(self.start, self.end)
        account_count = 0
        for account in accounts:
            self.assertIsInstance(account, Account)
            account_count += 1
        self.assertEqual(account_count, len(self.rows))


    def test_add_accounts(self):
        self.am.bulk_add = MagicMock()
        self.am.add_accounts(self.end)


    def tearDown(self):
        self.elasticsearch.stop()
