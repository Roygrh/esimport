################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import glob
import os
import random
import subprocess
import threading
import time
from datetime import datetime
from multiprocessing import Process
from operator import itemgetter
from unittest import TestCase

import chardet
import dateutil.parser
from elasticsearch import Elasticsearch
from mock import MagicMock, Mock, patch

import pyodbc
from esimport import settings, tests
from esimport.cache import CacheClient
from esimport.connectors.mssql import MsSQLConnector
from esimport.mappings.account import AccountMapping
from esimport.mappings.property import PropertyMapping
from esimport.models import ESRecord
from esimport.models.account import Account
from esimport.models.base import BaseModel
import pytest

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

        self.properties = tests._mocked_sql('esimport_properties.csv')[0]

        # for row in self.rows:
        #     row['Date_Modified_UTC'] = str(datetime.now())

        self.am = AccountMapping()
        self.am.setup()

        self.pm = PropertyMapping()
        self.pm.setup()
        # self.pm.get_property_by_org_number = MagicMock(return_value=self.properties)
        self.am.pm = self.pm

        self.start = 0
        for sql in glob.glob(test_dir + '/esimport/tests/fixtures/sql/*.sql'):
            # script = test_dir + "/esimport/tests/fixtures/sql/"+sql
            # subprocess.check_call(["sqlcmd", "-S", host, "-i", script, "-U", uid, "-P", pwd, "-d", db],
            #                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            with open(sql, 'b+r') as inp:
                sqlQuery = ''
                inp_b = inp.read()
                the_encoding = chardet.detect(inp_b)['encoding']
                inp = inp_b.decode(the_encoding).replace('GO', '')
                self.am.model.execute(inp)
            self.am.model.conn.reset()

        self.end = self.start + min(len(self.rows), self.am.step_size)

        # conn = Mock()
        # self.am.model = Account(conn)
        # self.am.model.conn.cursor = Mock()
        # self.am.model.conn.cursor.execute = MagicMock(return_value=self.rows)






        # needs ES_HOME set to where elastic search is downloaded
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)
        # self.am.es = self.es
        # self.am.pm.es = self.es

    # also an integration test

    def test_bulk_add_or_update(self):
        _index = Account.get_index()
        _type = Account.get_type()

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

        # Note: start and end inputs are ignored because test data is hard coded
        accounts = self.am.model.get_accounts_by_created_date(self.start, self.end)
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
        _index = f'{Account.get_index()}-{datetime.now().date().strftime("%Y-%m")}'
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
        acc1 = ESRecord(doc1, Account.get_type(), Account.get_index(), index_date=datetime.now().date())
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
        acc2 = ESRecord(doc2, Account.get_type(), Account.get_index(), index_date=datetime.now().date())
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
        _index = Account.get_index()

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

        self.assertTrue(isinstance(self.am.get_es_count(), int))

        es.indices.delete(index=_index, ignore=400)
        self.assertFalse(es.indices.exists(index=_index))

    def _give_me_some_data(self, es):
        # add accounts from mocked sql to ES
        self.am.add_accounts('1990-01-01')  # there is a delay

        total = self.am.get_es_count()
        retries = 0
        while total <= 0 and retries < self.am.esRetry:
            time.sleep(self.am.esTimeout)
            total = self.am.get_es_count()
            retries += 1

        return total > 0

    @pytest.mark.xfail(
        strict=True,
        reason="Test update document in ES, and trying to compare input value for ServiceArea with result "
        "that returned get_accounts_by_created_date(). But this method will return ServiceArea value from organization"
        " what means test will always fail."
    )
    def test_update_fields_data(self):
        _index = settings.ES_INDEX
        _type = Account.get_type()

        es = self.es
        es.indices.create(index=_index, ignore=400)
        self.assertTrue(es.indices.exists(index=_index))

        account_doc = {
            "_op_type": "update",
            "_index": "esrecord",
            "_type": "account",
            "_id": "1",
            "doc_as_upsert": True,
            "doc": {
                "ID": 1,
                "Name": "cc-9886_79C66442-7E37-4B0D-B512-E7D1C9EDFC11",
                "MemberNumber": "1",
                "Status": "Status",
                "ServiceArea": "00-00-00",
                "Price": 12.95,
                "PurchaseMacAddress": "34-C0-59-D8-31-08",
                "Activated": "2014-01-04T07:38:24.370000+00:00",
                "Created": "2014-01-04T07:38:24.357000+00:00",
                "UpsellAccountID": None,
                "DateModifiedUTC": "2018-05-02T09:15:11.237000+00:00",
                "ServicePlan": "basic day",
                "ServicePlanNumber": "basic_day_01",
                "UpCap": 1236,
                "DownCap": 4196,
                "NetworkAccessStartDateUTC": "2014-01-04T07:38:24.357000+00:00",
                "NetworkAccessEndDateUTC": "2018-04-05T10:31:46.767000+00:00",
                "PayMethod": "CC",
                "Currency": "AFA",
                "CreditCardNumber": None,
                "CardType": None,
                "LastName": "trava",
                "RoomNumber": "4051",
                "DiscountCode": "DC03",
                "ConsumableTime": 2,
                "ConsumableUnit": "Hours",
                "SpanTime": None,
                "SpanUnit": None,
                "ConnectCode": None,
                "MarketingContact": None,
                "ZoneType": None,
                "VLAN": 1,
                "Duration": "2 Hours consumable",
                "PropertyName": "some display name 1",
                "PropertyNumber": "GL-236-20",
                "Provider": None,
                "Brand": "Marriott",
                "MARSHA_Code": "BWIAK",
                "Country": "",
                "Region": "",
                "SubRegion": "",
                "OwnershipGroup": "",
                "TaxRate": "",
                "CorporateBrand": "",
                "ExtPropId": "",
                "TimeZone": "Asia/Dhaka",
                "CreatedLocal": "2014-01-04T13:38:24.357000+06:00",
                "ActivatedLocal": "2014-01-04T13:38:24.370000+06:00"
            }
        }

        am = AccountMapping()
        am.setup()

        am.add(account_doc, 1)

        account_doc_es = es.get(index=settings.ES_INDEX, id=1)
        account = am.model.get_accounts_by_created_date(1, 10)
        ac = next(account).es()
        self.assertEqual(ac['doc']['ServiceArea'], account_doc_es['_source']['ServiceArea'])

    @pytest.mark.skip(
        reason="Test broken Account.get_index() will return `accounts` but there will be no data in that index, "
        "because now index name is dynamic"
    )
    def test_property_mapping_fields(self):
        with patch.object(self.pm, 'get_property_by_org_number', return_value=self.properties) as mock_method:
            _index = Account.get_index()

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

    # currently not working, but also not being used in production
    #    def test_backload(self):
    #        _index = settings.ES_INDEX
    #        _type = Account.get_type()
    #
    #        es = self.es
    #        es.indices.create(index=_index, ignore=400)
    #        self.assertTrue(es.indices.exists(index=_index))
    #
    #        # load a fixture with data from 2012 - 2016
    #        data = tests._mocked_sql('esimport_accounts_2012_2016.csv')
    #
    #        _rows = self.am.model.get_accounts_by_created_date(self.start, self.end)
    #        # self.am.model.conn.cursor.execute = MagicMock(return_value=data)
    #
    #        start = 0
    #        limit = len(data)
    #        # needed because we need ESRecord by Account's model
    #        data = self.am.model.get_accounts_by_created_date(start, limit)
    #
    #        # call backload with start_date=2015-*
    #        start_date = datetime.strptime('2015-01-01', '%Y-%m-%d')
    #        dt_format = '%Y-%m-%dT%H:%M:%S.%f'
    #        filtered_data = map(lambda x: x if datetime.strptime(x.get('Created'), dt_format) >= start_date
    #                                        else None, data)
    #        filtered_data = list(filter(lambda x: x, filtered_data))
    #        _get_accounts = self.am.model.get_accounts_by_created_date(start, limit, start_date=start_date)
    #        # self.am.model.get_accounts = MagicMock(return_value=filtered_data)
    #        self.am.backload('2015-01-01')
    #
    #        # wait
    #        total = self.am.get_es_count()
    #        retries = 0
    #        while total <= 0 and retries < self.am.esRetry:
    #            time.sleep(self.am.esTimeout)
    #            total = self.am.get_es_count()
    #            retries += 1
    #        self.assertEqual(total, len(filtered_data))
    #
    #        # get existing records
    #        start = 0
    #        end = start + min(len(filtered_data), self.am.step_size)
    #        for rec in self.am.get_existing_accounts(start, end):
    #            # verify that only 2015-2016 data exists
    #            self.assertGreaterEqual(datetime.strptime(rec.get('Created'), dt_format), start_date)
    #
    #        self.am.model.get_accounts_by_created_date = _get_accounts
    #
    #        es.indices.delete(index=_index, ignore=400)
    #        self.assertFalse(es.indices.exists(index=_index))

    @pytest.mark.xfail(
        strict=True,
        reason="sync method runs in thread, it does not have time to sync data"
        "needs to be rewrite core logic to test")
    def test_sync_is_continuous(self):
        # need some mocked data
        # can't let thread modify global am
        rows = tests._mocked_sql('multiple_orders.csv')
        am = AccountMapping()
        am.model = Account(Mock())
        am.model.conn.cursor = Mock()
        am.model.conn.cursor.execute = MagicMock(return_value=rows)

        properties = tests._mocked_sql('esimport_properties.csv')[0]
        pm = PropertyMapping()
        pm.get_property_by_org_number = MagicMock(return_value=properties)
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
        t = threading.Thread(target=sync, args=(am,), daemon=True)
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

    @pytest.mark.skip(
        reason="New version of code should use aliases or dynamic indexes name, tests should be rewritten"
    )
    def test_date_modified_update(self):
        # TODO: although this test is "fixed" - passed without errors, it probably should test
        #  that if column `Date_Modified_UTC` in MSSQL changed, esimport detect that and update data in ES.
        #  Curently this test is fixed by using `update()` method that uses `Date_Created_UTC` column to select data.

        # backload db to elasticsearch
        self.am.backload(start_date='1900-01-01')
        self.pm.backload()

        am = AccountMapping()
        am.setup()

        initial_date = self.am.model.execute("""SELECT MIN(Date_Created_UTC) from Zone_Plan_Account""").fetchone()[
            0].strftime('%Y-%m-%d %H:%M:%S')

        am.update(initial_date)

        # check if zpa with id 1 exist
        zpa_1 = self.am.model.execute("""SELECT ID,Purchase_Price FROM Zone_Plan_Account WHERE ID=1""").fetchone()
        self.assertEqual(zpa_1[0], 1)

        # check elasticsearch if record exist
        query = {'query': {'term': {'ID': '1'}}}
        zpa_1_es = self.es.search(index=Account.get_index(), body=query)['hits']['hits']
        self.assertTrue(len(zpa_1_es) > 0)
        self.assertEqual(zpa_1_es[0]['_source']['ID'], 1)
        self.assertEqual(zpa_1_es[0]['_source']['Price'], float(zpa_1[1]))

        # change a record in db
        # current_time = datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f')[:-3]
        current_time = '2018-04-05 10:33:20.000'
        q = """UPDATE Zone_Plan_Account 
            SET Purchase_Price=13.0,Date_Modified_UTC=? 
            WHERE ID=1"""

        self.am.model.execute(q, current_time)
        zpa_1 = self.am.model.execute(
            """SELECT ID,Purchase_Price,Date_Modified_UTC FROM Zone_Plan_Account WHERE ID=1""").fetchone()

        am.update(initial_date)

        self.assertEqual(zpa_1[1], 13.0)
        zpa_1_es = self.es.search(index=Account.get_index(), body=query)['hits']['hits']
        self.assertEqual(zpa_1_es[0]['_source']['Price'], float(zpa_1[1]))

        # update multiple records
        q = """UPDATE Zone_Plan_Account
            SET Purchase_Price = CASE ID
                                    WHEN 1 THEN 20.0
                                    WHEN 2 THEN 30.0
                                    WHEN 3 THEN 40.0
                                END,
                Date_Modified_UTC = CASE ID
                                    WHEN 1 THEN '{0}'
                                    WHEN 2 THEN '{0}'
                                    WHEN 3 THEN '{0}'
                                END
            WHERE ID IN (1,2,3)""".format('2018-04-05 10:34:20.000')
        self.am.model.execute(q)

        query = {'query': {
            'terms': {'ID': ['1', '2', '3']}
        }
        }

        am.update(initial_date)

        zpa_123_es = self.es.search(index=Account.get_index(), body=query, doc_type='account')['hits']['hits']
        zpa_123 = self.am.model.execute(
            """SELECT ID,Purchase_Price FROM Zone_Plan_Account WHERE ID IN (1,2,3)""").fetchall()
        zpa_123.sort(key=itemgetter(0))
        for zpa in zpa_123_es:
            if zpa['_source']['ID'] == 1:
                self.assertEqual(zpa['_source']['Price'], float(zpa_123[0][1]))
            elif zpa['_source']['ID'] == 2:
                self.assertEqual(zpa['_source']['Price'], float(zpa_123[1][1]))
            elif zpa['_source']['ID'] == 3:
                self.assertEqual(zpa['_source']['Price'], float(zpa_123[2][1]))

    def test_esrecord_has_devices_members_count(self):
        count_query_by_id = self.pm.model.query_get_active_counts()
        props = [prop for prop in self.pm.model.get_properties(0, 2)]

        for prop in props:
            counts = self.am.model.execute(count_query_by_id, prop.record['ID']).fetchone()
            self.assertEqual(prop.record['ActiveMembers'], counts[0])
            self.assertEqual(prop.record['ActiveDevices'], counts[1])

    @pytest.mark.skip(
        reason="Test broken Account.get_index() will return `accounts` but there will be no data in that index, "
        "because now index name is dynamic"
    )
    def test_property_update_in_elasticsearch(self):
        # create index
        self.es.indices.create(index=Account.get_index(), ignore=400)

        pm = PropertyMapping()
        pm.setup()
        property_update = lambda _pm: _pm.update()
        t = threading.Thread(target=property_update, args=(pm,), daemon=True)
        t.start()

        # time to catch up
        time.sleep(1)

        property_list = []
        props = [prop for prop in self.pm.model.get_properties(0, 2)]
        for prop in props:
            property_list.append(prop.record)
        property_list.sort(key=itemgetter('ID'))

        # get all property from elasticsearch
        property_es_list = []
        query = {'query': {'term': {'_type': 'property'}}}
        property_es = self.es.search(index=settings.ES_INDEX, body=query)['hits']['hits']
        for prop in property_es:
            property_es_list.append(prop['_source'])
        property_es_list.sort(key=itemgetter('ID'))

        self.assertEqual(property_list[0]['ActiveMembers'], property_es_list[0]['ActiveMembers'])
        self.assertEqual(property_list[1]['ActiveMembers'], property_es_list[1]['ActiveMembers'])

    def test_redis_cache(self):
        # create index
        self.es.indices.create(index=settings.ES_INDEX, ignore=400)

        pm = PropertyMapping()
        pm.setup()
        property_update = lambda _pm: _pm.update()
        t = threading.Thread(target=property_update, args=(pm,), daemon=True)
        t.start()

        # time to catch up
        time.sleep(1)

        service_areas = []
        # check if property records are in redis
        property_list = [prop.record for prop in self.pm.model.get_properties(0, 2)]
        for prop in property_list:
            for service_area_obj in prop['ServiceAreaObjects']:
                service_areas.append(service_area_obj['Number'])
        for service_area in service_areas:
            self.assertTrue(self.pm.cache_client.exists(service_area))

        # check records are returning from redis rather than elasticsearch
        for service_area in service_areas:
            res = self.pm.cache_client.get(service_area)
            res['cache'] = True
            res['CreatedUTC'] = dateutil.parser.parse(res['CreatedUTC'])
            self.pm.cache_client.set(service_area, res)

        for service_area in service_areas:
            record = self.pm.get_property_by_org_number(service_area)
            if record:
                # import pdb
                # pdb.set_trace()
                self.assertTrue(record['cache'])

    def tearDown(self):


        self.am.model.execute("""
DECLARE @sql NVARCHAR(MAX);
SET @sql = N'';
SELECT @sql += 'ALTER TABLE ' + QUOTENAME(s.name) + N'.'
  + QUOTENAME(t.name) + N' DROP CONSTRAINT '
  + QUOTENAME(c.name) + ';'
FROM sys.objects AS c
INNER JOIN sys.tables AS t
ON c.parent_object_id = t.[object_id]
INNER JOIN sys.schemas AS s
ON t.[schema_id] = s.[schema_id]
WHERE c.[type] = 'F'
ORDER BY c.[type];
SELECT @sql += 'DROP TABLE ' + QUOTENAME([TABLE_SCHEMA]) + '.' + QUOTENAME([TABLE_NAME]) + ';'
FROM [INFORMATION_SCHEMA].[TABLES]
WHERE [TABLE_TYPE] = 'BASE TABLE';
EXEC SP_EXECUTESQL @sql;""")

        es = self.am.es
        if es.indices.exists(index=settings.ES_INDEX):
            es.indices.delete(index=settings.ES_INDEX, ignore=400)

        self.pm.cache_client.client.flushall()
