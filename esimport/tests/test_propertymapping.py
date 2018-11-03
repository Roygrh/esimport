################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import os
import glob
import threading
import time
import pytest
from unittest import TestCase
from elasticsearch import Elasticsearch

from six.moves import range
from mock import MagicMock

from esimport.mappings.property import PropertyMapping
from esimport import settings
from esimport.mappings.init_index import new_index


class TestPropertyMapping(TestCase):


    def setUp(self):
        test_dir = os.getcwd()
        host = settings.DATABASES['default']['HOST']
        uid = settings.DATABASES['default']['USER']
        pwd = settings.DATABASES['default']['PASSWORD']
        db = settings.DATABASES['default']['NAME']

        self.pm = PropertyMapping()
        self.pm.setup()

        for sql in glob.glob(test_dir+'/esimport/tests/fixtures/sql/*.sql'):
            with open(sql, 'r') as inp:
                sqlQuery = ''
                for line in inp:
                    if 'GO' not in line:
                        sqlQuery = sqlQuery + line
                self.pm.model.execute(sqlQuery)
                self.pm.model.conn.reset()
            inp.close()
            self.pm.model.conn.reset()

        # self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)
        self.es = self.pm.es

        ni = new_index()
        ni.setup()
        ni.setupindex()

        pm = PropertyMapping()
        pm.setup()
        sync = lambda _pm: _pm.sync()
        t = threading.Thread(target=sync, args=(pm,), daemon=True)
        t.start()

    def get_poperties(self):
        q = """Select Organization.ID as ID,
Organization.Contact_ID as ContactID
From Organization WITH (NOLOCK)
Where Organization.Org_Category_Type_ID = 3
    AND Organization.ID > 0
ORDER BY Organization.ID ASC"""
        s = self.pm.model.execute(q).fetchall()
        return s

    def test_property_data_in_es(self):
        time.sleep(2)

        q = {"query": {"term": {"_type": self.pm.model.get_type()}}}
        res = self.es.search(index=settings.ES_INDEX, body=q)['hits']['hits']
        property_id_es = [property['_source']['ID'] for property in res]
        property_id_es.sort()

        property_ids = [property_id[0] for property_id in self.get_poperties()].sort()

        self.assertEqual(property_id_es, property_id_es)

    def test_address_as_nested(self):
        time.sleep(2)

        q = {"query": {"term": {"_type": self.pm.model.get_type()}}}
        res = self.es.search(index=settings.ES_INDEX, body=q)['hits']['hits']

        addresses = res[0]['_source']['Address']

        address_keys = ['AddressLine1', 'AddressLine2', 'City', 'Area',
                        'PostalCode', 'CountryID', 'CountryName']

        self.assertEqual(set(address_keys), set(addresses.keys()))

    def test_property_address(self):
        time.sleep(2)

        properties = self.get_poperties()

        q = """SELECT Address.Address_1 as AddressLine1,
Address.Address_2 as AddressLine2,
Address.City,
Address.Area,
Address.Postal_Code as PostalCode,
Address.Country_ID as CountryID,
Country.Name as CountryName
FROM Organization
Left Join Contact_Address WITH (NOLOCK) ON Contact_Address.Contact_ID = {0}
Left Join Address WITH (NOLOCK) ON Address.ID = Contact_Address.Address_ID
Left Join Country WITH (NOLOCK) ON Country.ID = Address.Country_ID"""
        addresses = {}
        for prop in properties:
            res = self.pm.model.execute(q.format(prop[1])).fetchone()
            addresses[str(prop[0])] = {
                'AddressLine1': res[0],
                'AddressLine2': res[1],
                'City': res[2], 
                'Area': res[3],
                'PostalCode': res[4], 
                'CountryID': res[5], 
                'CountryName': res[6]
            }
        q = {"query": {"term": {"_type": self.pm.model.get_type()}}}
        res = self.es.search(index=settings.ES_INDEX, body=q)['hits']['hits']

        for prop in res:
            self.assertEqual(set(prop['_source']['Address']), set(addresses[prop['_id']]))

    # def test_add(self):
    #     pm1 = PropertyMapping()
    #     pm1.bulk_add_or_update = MagicMock()
    #     for i in range(0):
    #         pm1.add(dict(ii=i), 500)
    #     self.assertFalse(pm1.bulk_add_or_update.called)

    #     pm2 = PropertyMapping()
    #     pm2.bulk_add_or_update = MagicMock()
    #     for i in range(499):
    #         pm2.add(dict(ii=i), 500)
    #     self.assertFalse(pm2.bulk_add_or_update.called)

    #     pm3 = PropertyMapping()
    #     pm3.bulk_add_or_update = MagicMock()
    #     for i in range(500):
    #         pm3.add(dict(ii=i), 500)
    #     self.assertTrue(pm3.bulk_add_or_update.called)

    #     pm4 = PropertyMapping()
    #     pm4.bulk_add_or_update = MagicMock()
    #     for i in range(9):
    #         pm4.add(dict(ii=i), 10)
    #     self.assertFalse(pm4.bulk_add_or_update.called)

    #     pm5 = PropertyMapping()
    #     pm5.bulk_add_or_update = MagicMock()
    #     for i in range(10):
    #         pm5.add(dict(ii=i), 10)
    #     self.assertTrue(pm5.bulk_add_or_update.called)

    #     pm6 = PropertyMapping()
    #     pm6.bulk_add_or_update = MagicMock()
    #     for i in range(10):
    #         pm6.add(None, 10)
    #     self.assertFalse(pm6.bulk_add_or_update.called)

    def tearDown(self):
        self.pm.model.execute("""
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

        es = self.pm.es
        if es.indices.exists(index=settings.ES_INDEX):
            es.indices.delete(index=settings.ES_INDEX, ignore=400)

        self.pm.cache_client.client.flushall()