from unittest import TestCase

import testing.elasticsearch
from elasticsearch import Elasticsearch
from mock import Mock, MagicMock

from esimport.models.account import Account
from esimport.mappings.account import AccountMapping
from esimport import tests


"""
Separated because takes long to run
"""
class TestAccountMappingElasticSearch(TestCase):

    def setUp(self):
        self.rows = self.multiple_orders = tests._mocked_sql()

        self.am = AccountMapping()
        self.am.setup_config()
        self.start = self.am.position
        self.end = self.start + min(len(self.rows), self.am.step_size)
        self.am.cursor = Mock()
        self.am.cursor.execute = MagicMock(return_value=self.rows)

        # needs ES_HOME set to where elastic search is downloaded
        self.elasticsearch = testing.elasticsearch.Elasticsearch()


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


    def tearDown(self):
        self.elasticsearch.stop()
