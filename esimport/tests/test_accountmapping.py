from unittest import TestCase

from elasticsearch import Elasticsearch
from mock import Mock, MagicMock

from esimport.models.account import Account
from esimport.mappings.account import AccountMapping
from esimport import tests


class TestAccountMapping(TestCase):

    def setUp(self):
        self.rows = self.multiple_orders = tests._mocked_sql()

        self.am = AccountMapping()
        self.am.setup_config()
        self.start = 0
        self.end = self.start + min(len(self.rows), self.am.step_size)
        self.am.cursor = Mock()
        self.am.cursor.execute = MagicMock(return_value=self.rows)


    def test_setup_config(self):
        am = AccountMapping()

        assert am.step_size is None
        assert am.esTimeout is None
        assert am.esRetry is None

        am.setup_config()

        assert am.step_size is not None
        assert am.esTimeout is not None
        assert am.esRetry is not None

        am.setup_config()


    def test_bulk_add_retry(self):
        wrong_dsn = {'hosts': ['127.0.0.1:57288']}
        es = Elasticsearch(**wrong_dsn)

        # Note: start and end inputs are ignored because test data is hard coded
        accounts = self.am.get_accounts(self.start, self.end)
        actions = [account.action for account in accounts]

        attempts = self.am.bulk_add_or_update(es, actions, 1, self.am.esTimeout)
        self.assertGreater(attempts, 0)


    # whether returned result count is equal to request count
    def test_get_accounts(self):
        accounts = self.am.get_accounts(self.start, self.end)
        account_count = 0
        for account in accounts:
            self.assertIsInstance(account, Account)
            account_count += 1
        self.assertEqual(account_count, len(self.rows))

