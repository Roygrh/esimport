################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import six
import time
import threading
import random
import pyodbc
import os
import subprocess
from multiprocessing import Process

from unittest import TestCase
from datetime import datetime
from operator import itemgetter

from elasticsearch import Elasticsearch
from mock import Mock, MagicMock

from esimport.models import ESRecord
from esimport.models.account import Account
from esimport.models.base import BaseModel
from esimport.mappings.account import AccountMapping
from esimport.mappings.property import PropertyMapping
from esimport.connectors.mssql import MsSQLConnector
from esimport import tests
from esimport import settings


"""
Separated because takes long to run
"""
class TestAccountMappingElasticSearch(TestCase):

    maxDiff = None


    def setUp(self):
        # sqlcmd -S localhost -i esimport/tests/fixtures/sql/zone_plan_account.sql -U SA -P <password> -d Eleven_OS
        test_dir = os.getcwd()
        host = settings.DATABASES['default']['HOST']
        uid = settings.DATABASES['default']['USER']
        pwd = settings.DATABASES['default']['PASSWORD']
        db = settings.DATABASES['default']['NAME']

        self.rows = tests._mocked_sql('multiple_orders.csv')

        # for row in self.rows:
        #     row['Date_Modified_UTC'] = str(datetime.now())

        self.am = AccountMapping()
        self.am.setup()
        self.start = 0
        for sql in os.listdir(test_dir+'/esimport/tests/fixtures/sql/'):
            script = test_dir + "/esimport/tests/fixtures/sql/"+sql
            # subprocess.check_call(["sqlcmd", "-S", host, "-i", script, "-U", uid, "-P", pwd, "-d", db], 
            #                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            with open(script, 'r') as inp:
                sqlQuery = ''
                for line in inp:
                    if 'GO' not in line:
                        sqlQuery = sqlQuery + line
                self.am.model.execute(sqlQuery).commit()
            inp.close()

        self.end = self.start + min(len(self.rows), self.am.step_size)


        # conn = Mock()
        # self.am.model = Account(conn)
        # self.am.model.conn.cursor = Mock()
        # self.am.model.conn.cursor.execute = MagicMock(return_value=self.rows)

        # self.properties = tests._mocked_sql('esimport_properties.csv')

        # self.pm = PropertyMapping()
        # self.pm.get_properties_by_service_area = MagicMock(return_value=self.properties)
        # self.am.pm = self.pm

        # needs ES_HOME set to where elastic search is downloaded
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)
        # self.am.es = self.es
        # self.am.pm.es = self.es


    # also an integration test
    def test_bulk_add_or_update(self):
        _index = settings.ES_INDEX
        _type = Account.get_type()

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

        # Note: start and end inputs are ignored because test data is hard coded
        accounts = self.am.model.get_accounts(self.start, self.end)
        for a in accounts:
            print(a)
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
                    RoomNumber=101,
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
                    RoomNumber=101,
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

        if six.PY2:
            self.assertTrue(isinstance(self.am.get_es_count(), (int, long)))
        else:
            self.assertTrue(isinstance(self.am.get_es_count(), int))

        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))


    def _give_me_some_data(self, es):
        # add accounts from mocked sql to ES
        self.am.add_accounts('1990-01-01') # there is a delay

        total = self.am.get_es_count()
        retries = 0
        while total <= 0 and retries < self.am.esRetry:
            time.sleep(self.am.esTimeout)
            total = self.am.get_es_count()
            retries += 1

        return total > 0


    def test_update_new_fields_only(self):
        _index = settings.ES_INDEX
        _type = Account.get_type()

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

        self.assertTrue(self._give_me_some_data(es))

        # create mocked sql with new field(s) (Org=SkyNet)
        updated_records = tests.Records()
        for r in range(0, len(self.rows), 2):
            row = self.rows[r]
            updated_records.setKeys(row.keys())
            row['Org'] = 'SkyNet'
            updated_records.append(row)

        limit = self.am.get_es_count()

        # get updated records from mocked sql and verify length
        _rows = self.am.model.conn.cursor.execute
        self.am.model.conn.cursor.execute = MagicMock(return_value=updated_records)
        actions = list(self.am.get_updated_records(self.start, limit))
        self.assertEqual(len(actions), len(updated_records))

        # check if all updated_records (actions) has _id
        for action in actions:
            self.assertIn('_id', action)
            self.assertIsNotNone('_id', action)

        # update ES records with new fields only
        self.am.update()

        # verify only records with new fields were updated
        for r in self.rows:
            doc_saved = es.get(index=_index, doc_type=_type, id=r.get('ID')).get('_source', {})
            updated_record = any(filter(lambda x: x.get('ID') == doc_saved.get('ID'), updated_records))
            if updated_record:
                self.assertIn('Org', doc_saved)
            else:
                self.assertNotIn('Org', doc_saved)

        self.am.model.conn.cursor.execute = _rows

        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))


    def test_property_mapping_fields(self):
        _index = settings.ES_INDEX

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

        self.assertTrue(self._give_me_some_data(es))

        for rec in self.am.get_existing_accounts(self.start, self.end):
            records_with_properties = [pfik in rec for pfik, pfiv in self.am.property_fields_include]
            self.assertEqual(len(records_with_properties), len(self.am.property_fields_include))
            # some redundant code is to test iterator exhaustion
            self.assertTrue(all([pfik in rec for pfik, pfiv in self.am.property_fields_include]))

        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))


    def test_backload(self):
        _index = settings.ES_INDEX
        _type = Account.get_type()

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

        # load a fixture with data from 2012 - 2016
        data = tests._mocked_sql('esimport_accounts_2012_2016.csv')

        _rows = self.am.model.get_accounts(self.start, self.end)
        # self.am.model.conn.cursor.execute = MagicMock(return_value=data)

        start = 0
        limit = len(data)
        # needed because we need ESRecord by Account's model
        data = self.am.model.get_accounts(start, limit)

        # call backload with start_date=2015-*
        start_date = datetime.strptime('2015-01-01', '%Y-%m-%d')
        dt_format = '%Y-%m-%d %H:%M:%S.%f'
        filtered_data = map(lambda x: x if datetime.strptime(x.get('Created'), dt_format) >= start_date
                                        else None, data)
        filtered_data = list(filter(lambda x: x, filtered_data))
        _get_accounts = self.am.model.get_accounts(start, limit, start_date=start_date)
        # self.am.model.get_accounts = MagicMock(return_value=filtered_data)
        self.am.backload('2015-01-01')

        # wait
        total = self.am.get_es_count()
        retries = 0
        while total <= 0 and retries < self.am.esRetry:
            time.sleep(self.am.esTimeout)
            total = self.am.get_es_count()
            retries += 1
        self.assertEqual(total, len(filtered_data))

        # get existing records
        start = 0
        end = start + min(len(filtered_data), self.am.step_size)
        for rec in self.am.get_existing_accounts(start, end):
            # verify that only 2015-2016 data exists
            self.assertGreaterEqual(datetime.strptime(rec.get('Created'), dt_format), start_date)

        self.am.model.get_accounts = _get_accounts

        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))


    def test_sync_is_continuous(self):
        # need some mocked data
        # can't let thread modify global am
        rows = tests._mocked_sql('multiple_orders.csv')
        am = AccountMapping()
        am.model = Account(Mock())
        am.model.conn.cursor = Mock()
        am.model.conn.cursor.execute = MagicMock(return_value=rows)

        properties = tests._mocked_sql('esimport_properties.csv')
        pm = PropertyMapping()
        pm.get_properties_by_service_area = MagicMock(return_value=properties)
        am.pm = pm

        # setup ES
        _index = settings.ES_INDEX
        _type = Account.get_type()

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))
        am.es = es
        am.pm.es = es

        # run sync in different thread
        sync = lambda _am: _am.sync('1900-01-01')
        kwargs = dict()
        if not six.PY2:
            kwargs = dict(daemon=True)
        t = threading.Thread(target=sync, args=(am,), **kwargs)
        if six.PY2:
            t.daemon = True
        t.start()

        # verify data was sync
        total = am.get_es_count()
        retries = 0
        while total <= 0 and retries < am.esRetry:
            time.sleep(am.esTimeout)
            total = am.get_es_count()
            retries += 1
        self.assertEqual(total, len(self.rows))

        # verify if sync thread is still running
        self.assertTrue(t.is_alive())

        # load a fixture from higher number ids
        data = tests._mocked_sql('esimport_accounts_new_data.csv')

        # change get_accounts again
        am.model.conn.cursor.execute = MagicMock(return_value=data)

        # verify new data was sync
        total = am.get_es_count()
        retries = 0
        while (total <= 0 or total <= len(self.rows)) and retries < am.esRetry:
            time.sleep(am.esTimeout)
            total = am.get_es_count()
            retries += 1
        self.assertEqual(total, len(self.rows) + len(data))

        # delete _index
        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))


    def test_date_modified_update(self):
        # backload db to elasticsearch
        self.am.backload(start_date='1900-01-01')
        am = AccountMapping()
        am.setup()
        check_time_change = lambda _am: _am.check_for_time_change()
        t = threading.Thread(target=check_time_change, args=(am,), daemon=True)
        t.start()

        # check if zpa with id 1 exist
        zpa_1 = self.am.model.execute("""SELECT ID,Purchase_Price FROM Zone_Plan_Account WHERE ID=1""").fetchone()
        self.assertEqual(zpa_1[0], 1)

        # check elasticsearch if record exist
        query = {'query': {'term': {'ID': '1'}}}
        zpa_1_es = self.es.search(index=settings.ES_INDEX, body=query)['hits']['hits']
        self.assertTrue(len(zpa_1_es) > 0)
        self.assertEqual(zpa_1_es[0]['_source']['ID'], 1)
        self.assertEqual(zpa_1_es[0]['_source']['Price'], float(zpa_1[1]))
        

        # change a record in db
        current_time = datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f')[:-3]
        q = """UPDATE Zone_Plan_Account 
            SET Purchase_Price=13.0,Date_Modified_UTC=? 
            WHERE ID=1"""

        self.am.model.execute(q, current_time).commit()
        
        zpa_1 = self.am.model.execute("""SELECT ID,Purchase_Price FROM Zone_Plan_Account WHERE ID=1""").fetchone()
        self.assertEqual(zpa_1[1], 13.0)
        time.sleep(1)
        zpa_1_es = self.es.search(index=settings.ES_INDEX, body=query)['hits']['hits']
        self.assertEqual(zpa_1_es[0]['_source']['Price'], float(zpa_1[1]))

        # update multiple records
        q = """UPDATE Zone_Plan_Account
            SET Purchase_Price = CASE ID
                                    WHEN 1 THEN 20.0
                                    WHEN 2 THEN 30.0
                                    WHEN 3 THEN 40.0
                                END,
                Date_Modified_UTC = CASE ID
                                    WHEN 1 THEN ?
                                    WHEN 2 THEN ?
                                    WHEN 3 THEN ?
                                END
            WHERE ID IN (1,2,3)"""
        self.am.model.execute(q, datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f')[:-3], 
                                 datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f')[:-3],
                                 datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f')[:-3]).commit()

        query = {'query': {
                    'terms': {'ID': ['1','2','3']}
                }
        }
        time.sleep(1)
        zpa_123_es = self.es.search(index=settings.ES_INDEX, body=query)['hits']['hits']
        zpa_123 = self.am.model.execute("""SELECT ID,Purchase_Price FROM Zone_Plan_Account WHERE ID IN (1,2,3)""").fetchall()
        zpa_123.sort(key=itemgetter(0))
        for zpa in zpa_123_es:
            if zpa['_source']['ID'] == 1:
                self.assertEqual(zpa['_source']['Price'], zpa_123[0][1])
            elif zpa['_source']['ID'] == 2:
                self.assertEqual(zpa['_source']['Price'], zpa_123[1][1])
            elif zpa['_source']['ID'] == 3:
                self.assertEqual(zpa['_source']['Price'], zpa_123[2][1])


    def tearDown(self):
        self.am.model.execute("""DROP TABLE [dbo].[Code]
DROP TABLE [dbo].[Credit_Card_Type]
DROP TABLE [dbo].[Credit_Card]
DROP TABLE [dbo].[Currency]
DROP TABLE [dbo].[Member_Marketing_Opt_In]
DROP TABLE [dbo].[Member_Status]
DROP TABLE [dbo].[Member]
DROP TABLE [dbo].[Network_Access_Limits]
DROP TABLE [dbo].[Org_Value]
DROP TABLE [dbo].[Organization]
DROP TABLE [dbo].[Payment_Method]
DROP TABLE [dbo].[PMS_Charge]
DROP TABLE [dbo].[Prepaid_Zone_Plan]
DROP TABLE [dbo].[Promotional_Code]
DROP TABLE [dbo].[Time_Unit]
DROP TABLE [dbo].[Zone_Plan_Account_Promotional_Code]
DROP TABLE [dbo].[Zone_Plan_Account]
DROP TABLE [dbo].[Zone_Plan]""").commit()
        es = self.am.es
        if es.indices.exists(index=settings.ES_INDEX):
            es.indices.delete(index=settings.ES_INDEX, ignore=400)
