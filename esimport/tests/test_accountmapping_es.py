from unittest import TestCase
from datetime import datetime
from collections import namedtuple

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
        self.start = 0
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


    def test_upsert(self):
        es = Elasticsearch(**self.elasticsearch.dsn())

        _index = Account.get_index()
        _type = Account.get_type()

        doc1 = dict(ID=1, Name="cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11", LastName=None,
                    Created=datetime.now().date(),
                    Activated=datetime.now().date(),
                    Property="FF-471-20", Price=12.95, Currency="USD", PayMethod="",
                    RoomNumber=101, AccessCodeUsed=None,
                    PurchaseMacAddress="34-C0-59-D8-31-08",
                    UpCap=4096, DownCap=4096,
                    CreditCardNumber=None, CardType=None)
        doc1_tuple = namedtuple('GenericDict', doc1.keys())(**doc1)
        acc1 = Account(doc1_tuple)
        self.am.bulk_add(es, [acc1.action], self.am.esRetry, self.am.esTimeout)
        doc1_saved = es.get(index=_index, doc_type=_type, id=acc1.ID).get('_source', {})
        doc1_saved_price = float(doc1_saved.get('Price').replace(doc1_tuple.Currency, ''))

        doc2 = dict(ID=1, Name="cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11", LastName=None,
                    Created=datetime.now().date(),
                    Activated=datetime.now().date(),
                    Property="FF-471-20", Price=4, Currency="USD", PayMethod="",
                    RoomNumber=101, AccessCodeUsed=None,
                    PurchaseMacAddress="34-C0-59-D8-31-08",
                    UpCap=12288, DownCap=12288,
                    CreditCardNumber=None, CardType=None)
        doc2_tuple = namedtuple('GenericDict', doc2.keys())(**doc2)
        acc2 = Account(doc2_tuple)
        self.am.bulk_add(es, [acc2.action], self.am.esRetry, self.am.esTimeout)
        # note: getting by acc1.ID here
        doc2_saved = es.get(index=_index, doc_type=_type, id=acc1.ID).get('_source', {})
        doc2_saved_price = float(doc2_saved.get('Price').replace(doc2_tuple.Currency, ''))

        self.assertNotEqual(doc1_saved_price, doc2_saved_price)
        self.assertGreater(doc1_saved_price, doc2_saved_price)
        self.assertGreater(doc2_saved.get('UpCap'), doc1_saved.get('UpCap'))
        self.assertGreater(doc2_saved.get('DownCap'), doc1_saved.get('DownCap'))


    def tearDown(self):
        self.elasticsearch.stop()
