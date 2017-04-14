import six
import time

from unittest import TestCase
from datetime import datetime

from elasticsearch import Elasticsearch
from mock import Mock, MagicMock

from esimport.models import ESRecord
from esimport.models.account import Account
from esimport.mappings.account import AccountMapping
from esimport import tests
from esimport import settings


"""
Separated because takes long to run
"""
class TestAccountMappingElasticSearch(TestCase):

    maxDiff = None


    def setUp(self):
        self.rows = self.multiple_orders = tests._mocked_sql()

        self.am = AccountMapping()
        self.start = 0
        self.end = self.start + min(len(self.rows), self.am.step_size)

        conn = Mock()
        self.am.model = Account(conn)
        self.am.model.cursor.execute = MagicMock(return_value=self.rows)

        # needs ES_HOME set to where elastic search is downloaded
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)


    # also an integration test
    def test_bulk_add_or_update(self):
        _index = settings.ES_INDEX
        _type = Account.get_type()

        es = self.es
        es.indices.create(index=_index)
        self.assertTrue(es.indices.exists(index=_index))

        # Note: start and end inputs are ignored because test data is hard coded
        accounts = self.am.model.get_accounts(self.start, self.end)
        actions = [account.es() for account in accounts]
        self.am.bulk_add_or_update(es, actions, self.am.esRetry, self.am.esTimeout)

        for action in actions:
            es_record = es.get(index=_index, doc_type=_type, id=action.get('_id'))
            input_doc = action.get('doc', {})
            saved_doc = es_record.get('_source', {})
            self.assertEqual(input_doc, saved_doc)

        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))


    def test_upsert(self):
        _index = settings.ES_INDEX
        _type = Account.get_type()

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

        doc1 = dict(ID=1, Name="cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11", LastName=None,
                    Created=datetime.now().date(),
                    Activated=datetime.now().date(),
                    ServiceArea="FF-471-20", Price=12.95, Currency="USD", PayMethod="",
                    RoomNumber=101, AccessCodeUsed=None,
                    PurchaseMacAddress="34-C0-59-D8-31-08",
                    ServicePlan="One Day Pass", ServicePlanNumber="1dp_02",
                    UpCap=4096, DownCap=4096,
                    CreditCardNumber=None, CardType=None, ZoneType="GuestRoom",
                    DiscountCode="NANO", ConsumableTime=0, ConsumableUnit='Minutes',
                    SpanTime=0, SpanUnit='Days')
        acc1 = ESRecord(doc1, Account.get_type())
        self.am.bulk_add_or_update(es, [acc1.es()], self.am.esRetry, self.am.esTimeout)
        doc1_saved = es.get(index=_index, doc_type=_type, id=doc1.get('ID')).get('_source', {})
        doc1_saved_price = float(str(doc1_saved.get('Price')).replace(doc1.get('Currency'), ''))

        doc2 = dict(ID=1, Name="cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11", LastName=None,
                    Created=datetime.now().date(),
                    Activated=datetime.now().date(),
                    ServiceArea="FF-471-20", Price=4, Currency="USD", PayMethod="",
                    RoomNumber=101, AccessCodeUsed=None,
                    PurchaseMacAddress="34-C0-59-D8-31-08",
                    ServicePlan="Weekly Pass", ServicePlanNumber="1week_16",
                    UpCap=12288, DownCap=12288,
                    CreditCardNumber=None, CardType=None, ZoneType="Meeting",
                    DiscountCode="TPASS072", ConsumableTime=0, ConsumableUnit='Minutes',
                    SpanTime=0, SpanUnit='Days')
        acc2 = ESRecord(doc2, Account.get_type())
        self.am.bulk_add_or_update(es, [acc2.es()], self.am.esRetry, self.am.esTimeout)
        # note: getting by acc1.get('ID') here
        doc2_saved = es.get(index=_index, doc_type=_type, id=doc2.get('ID')).get('_source', {})
        doc2_saved_price = float(str(doc2_saved.get('Price')).replace(doc2.get('Currency'), ''))

        self.assertNotEqual(doc1_saved_price, doc2_saved_price)
        self.assertGreater(doc1_saved_price, doc2_saved_price)
        self.assertGreater(doc2_saved.get('UpCap'), doc1_saved.get('UpCap'))
        self.assertGreater(doc2_saved.get('DownCap'), doc1_saved.get('DownCap'))

        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))


    def test_get_es_count(self):
        _index = settings.ES_INDEX

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

        _es = self.am.es
        self.am.es = es
        if six.PY2:
            self.assertTrue(isinstance(self.am.get_es_count(), (int, long)))
        else:
            self.assertTrue(isinstance(self.am.get_es_count(), int))
        self.am.es = _es

        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))


    def test_update_new_fields_only(self):
        _index = settings.ES_INDEX
        _type = Account.get_type()

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

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
        updated_records = tests.Records()
        for r in range(0, len(self.rows), 2):
            row = self.rows[r]
            updated_records.setKeys(row.keys())
            row['Org'] = 'SkyNet'
            updated_records.append(row)

        # get updated records from mocked sql and verify length
        _rows = self.am.model.cursor.execute
        self.am.model.cursor.execute = MagicMock(return_value=updated_records)
        actions = list(self.am.get_updated_records(self.start, limit))
        self.assertEqual(len(actions), len(updated_records))

        # check if all updated_records (actions) has _id
        for action in actions:
            self.assertIn('_id', action)
            self.assertIsNotNone('_id', action)

        # update ES records with new fields only
        self.am.bulk_update(limit)

        # verify only records with new fields were updated
        for r in self.rows:
            doc_saved = es.get(index=_index, doc_type=_type, id=r.get('ID')).get('_source', {})
            updated_record = any(filter(lambda x: x.get('ID') == doc_saved.get('ID'), updated_records))
            if updated_record:
                self.assertIn('Org', doc_saved)
            else:
                self.assertNotIn('Org', doc_saved)

        self.am.model.cursor.execute = _rows
        self.am.es = _es

        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))


    def tearDown(self):
        es = self.es
        if es.indices.exists(index=settings.ES_INDEX):
            es.indices.delete(index=settings.ES_INDEX, ignore=400)
