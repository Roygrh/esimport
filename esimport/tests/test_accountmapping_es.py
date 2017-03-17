import six
import time

from unittest import TestCase
from datetime import datetime
from collections import namedtuple

import testing.elasticsearch5
from elasticsearch import Elasticsearch
from mock import Mock, MagicMock

from esimport.models.account import Account
from esimport.mappings.account import AccountMapping
from esimport import tests
from esimport import settings


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
        self.elasticsearch = testing.elasticsearch5.Elasticsearch()


    # also an integration test
    def test_bulk_add_or_update(self):
        es = Elasticsearch(**self.elasticsearch.dsn())
        es.indices.create(index=settings.ES_INDEX, ignore=400)

        # Note: start and end inputs are ignored because test data is hard coded
        accounts = self.am.get_accounts(self.start, self.end)
        actions = [account.action for account in accounts]
        self.am.bulk_add_or_update(es, actions, self.am.esRetry, self.am.esTimeout)

        _index = settings.ES_INDEX
        _type = Account.get_type()
        for action in actions:
            es_record = es.get(index=_index, doc_type=_type, id=action.get('_id'))
            input_doc = action.get('doc', {})
            saved_doc = es_record.get('_source', {})
            self.assertEqual(input_doc, saved_doc)


    def test_upsert(self):
        es = Elasticsearch(**self.elasticsearch.dsn())
        es.indices.create(index=settings.ES_INDEX, ignore=400)

        _index = settings.ES_INDEX
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
        self.am.bulk_add_or_update(es, [acc1.action], self.am.esRetry, self.am.esTimeout)
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
        self.am.bulk_add_or_update(es, [acc2.action], self.am.esRetry, self.am.esTimeout)
        # note: getting by acc1.ID here
        doc2_saved = es.get(index=_index, doc_type=_type, id=acc1.ID).get('_source', {})
        doc2_saved_price = float(doc2_saved.get('Price').replace(doc2_tuple.Currency, ''))

        self.assertNotEqual(doc1_saved_price, doc2_saved_price)
        self.assertGreater(doc1_saved_price, doc2_saved_price)
        self.assertGreater(doc2_saved.get('UpCap'), doc1_saved.get('UpCap'))
        self.assertGreater(doc2_saved.get('DownCap'), doc1_saved.get('DownCap'))


    def test_get_es_count(self):
        es = Elasticsearch(**self.elasticsearch.dsn())
        es.indices.create(index=settings.ES_INDEX, ignore=400)

        _es = self.am.es
        self.am.es = es
        if six.PY2:
            self.assertTrue(isinstance(self.am.get_es_count(), (int, long)))
        else:
            self.assertTrue(isinstance(self.am.get_es_count(), int))
        self.am.es = _es


    def test_update_new_fields_only(self):
        _index = settings.ES_INDEX
        _type = Account.get_type()

        es = Elasticsearch(**self.elasticsearch.dsn())
        es.indices.create(index=_index, ignore=400)

        _es = self.am.es
        self.am.es = es

        # add accounts from mocked sql to ES
        max_id = self.am.max_id()
        self.am.add_accounts(max_id) # there is a delay

        limit = total = self.am.get_es_count()
        retries = 0
        while total <= 0 and retries < self.am.esRetry:
            time.sleep(self.am.esTimeout)
            limit = total = self.am.get_es_count()
            retries += 1

        # create mocked sql with new field(s) (Org=SkyNet)
        updated_records = None
        for r in range(0, len(self.rows), 2):
            row = self.rows[r]._asdict()
            row['Org'] = 'SkyNet'
            column_names = row.keys()
            if updated_records is None:
                updated_records = tests.Records(keys=column_names)
            row_tuple = namedtuple('GenericDict', column_names)(**row)
            updated_records.append(row_tuple)

        # get updated records from mocked sql and verify length
        _rows = self.am.cursor.execute
        self.am.cursor.execute = MagicMock(return_value=updated_records)
        actions = list(self.am.get_updated_records(self.start, limit))
        self.assertEqual(len(actions), len(updated_records))

        # update ES records with new fields only
        self.am.bulk_update(limit)

        # verify only records with new fields were updated
        for r in self.rows:
            doc_saved = es.get(index=_index, doc_type=_type, id=r.ID).get('_source', {})
            updated_record = any(filter(lambda x: x.ID == doc_saved.get('ID'), updated_records))
            if updated_record:
                self.assertIn('Org', doc_saved)
            else:
                self.assertNotIn('Org', doc_saved)

        self.am.cursor.execute = _rows
        self.am.es = _es

    def tearDown(self):
        self.elasticsearch.stop()
