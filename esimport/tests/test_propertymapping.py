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

import chardet
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
            with open(sql, 'b+r') as inp:
                sqlQuery = ''
                inp_b = inp.read()
                the_encoding = chardet.detect(inp_b)['encoding']
                inp = inp_b.decode(the_encoding).replace('GO', '')
                self.pm.model.execute(inp)
            self.pm.model.conn.reset()

        self.es = self.pm.es

        ni = new_index()
        ni.setup()
        ni.create_index()

        pm = PropertyMapping()
        pm.setup()
        sync = lambda _pm: _pm.sync()
        t = threading.Thread(target=sync, args=(pm,), daemon=True)
        t.start()

    def test_property_data_in_es(self):
        time.sleep(2)

        q = {"query": {"term": {"_type": self.pm.model.get_type()}}}
        res = self.es.search(index=settings.ES_INDEX, body=q)['hits']['hits']
        property_id_es = [property['_source']['ID'] for property in res]
        property_id_es.sort()

        properties = self.pm.model.fetch(self.pm.model.query_get_properties(), 10, 0)
        property_ids = [prop.ID for prop in properties]
        property_ids.sort()
        self.assertEqual(property_ids, property_id_es)

    def test_address_as_nested(self):
        time.sleep(2)

        q = {"query": {"term": {"_type": self.pm.model.get_type()}}}
        res = self.es.search(index=settings.ES_INDEX, body=q)['hits']['hits']

        addresses = res[0]['_source']['Address']

        address_keys = ['AddressLine1', 'AddressLine2', 'City', 'Area',
                        'PostalCode', 'CountryName']

        self.assertEqual(set(address_keys), set(addresses.keys()))

    def test_property_service_area_objects(self):
        time.sleep(2)

        service_area_lookup = {}

        properties = list(self.pm.model.fetch(self.pm.model.query_get_properties(), 10, 0))

        for prop in properties:
            service_areas = list(self.pm.model.fetch(self.pm.model.query_get_service_areas(), prop.ID))
            service_areas_arr = []

            for service_area in service_areas:
                service_area_dict = {
                    'Number': service_area.Number,
                    'Name': service_area.Name,
                    'ZoneType': service_area.ZoneType,
                    'ActiveMembers': service_area.ActiveMembers,
                    'ActiveDevices': service_area.ActiveDevices
                }

                hosts = list(self.pm.model.fetch(self.pm.model.query_get_service_area_devices(), service_area.ID))
                hosts_arr = []
                for host in hosts:
                    host_dict = {
                        "NASID": host.NASID,
                        "RadiusNASID": host.RadiusNASID,
                        "HostType": host.HostType,
                        "VLANRangeStart": host.VLANRangeStart,
                        "VLANRangeEnd": host.VLANRangeEnd,
                        "NetIP":host.NetIP
                    }

                    hosts_arr.append(host_dict)

                service_area_dict['Hosts'] = hosts_arr
                service_areas_arr.append(service_area_dict)

            service_area_lookup[str(prop.ID)] = service_areas_arr

        q = {"query": {"term": {"_type": self.pm.model.get_type()}}}
        res = self.es.search(index=settings.ES_INDEX, body=q)['hits']['hits']

        for prop in res:
            self.assertEqual(prop['_source']['ServiceAreaObjects'], service_area_lookup[prop['_id']])

    def test_property_address(self):
        time.sleep(2)

        properties = self.pm.model.fetch(self.pm.model.query_get_properties(), 10, 0)

        addresses = {}
        for prop in properties:
            addresses[str(prop.ID)] = {
                'AddressLine1': prop.AddressLine1,
                'AddressLine2': prop.AddressLine2,
                'City': prop.City, 
                'Area': prop.Area,
                'PostalCode': prop.PostalCode, 
                'CountryName': prop.CountryName
            }
        q = {"query": {"term": {"_type": self.pm.model.get_type()}}}
        res = self.es.search(index=settings.ES_INDEX, body=q)['hits']['hits']

        for prop in res:
            self.assertEqual(set(prop['_source']['Address']), set(addresses[prop['_id']]))

    def test_service_plans_in_service_area(self):
        time.sleep(2)

        properties = self.pm.model.fetch(self.pm.model.query_get_properties(), 10, 0)
        
        prop_mapping = {}

        for prop in list(properties):
            q_serviceplans = self.pm.model.query_get_service_area_serviceplans()
            for service_plan in list(self.pm.model.fetch(q_serviceplans, prop.ID)):
                sp_dic = {
                    "Number": service_plan.Number,
                    "Name": service_plan.Name,
                    "Description": service_plan.Description,
                    "Price": float(service_plan.Price),
                    "UpKbs": service_plan.UpKbs,
                    "DownKbs": service_plan.DownKbs,
                    "IdleTimeout": service_plan.IdleTimeout,
                    "ConnectionLimit": service_plan.ConnectionLimit,
                    "RadiusClass": service_plan.RadiusClass,
                    "GroupBandwidthLimit": service_plan.GroupBandwidthLimit,
                    "Type": service_plan.Type,
                    "PlanTime": service_plan.PlanTime,
                    "PlanUnit": service_plan.PlanUnit,
                    "LifespanTime": service_plan.LifespanTime,
                    "LifespanUnit": service_plan.LifespanUnit,
                    "CurrencyCode": service_plan.CurrencyCode,
                    "Status": service_plan.Status,
                    "OrgCode": service_plan.OrgCode,
                    "DateCreatedUTC": service_plan.DateCreatedUTC.isoformat()
                }
                    
            q_serviceareas = self.pm.model.query_get_service_areas()
            for service_area in list(self.pm.model.fetch(q_serviceareas, prop.ID)):
                if service_area.ID in prop_mapping.keys():
                    prop_mapping[prop.ID].append(sp_dic)
                else:
                    prop_mapping[prop.ID] = [sp_dic]

        q = {"query": {"term": {"_type": self.pm.model.get_type()}}}
        res = self.es.search(index=settings.ES_INDEX, body=q)['hits']['hits']

        for r in res:
            for sa in r['_source']['ServiceAreaObjects']:
                if sa.get('ServicePlans'):
                    self.assertListEqual(prop_mapping[int(r['_id'])], sa['ServicePlans'])

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
#         self.pm.model.execute("""
# DECLARE @sql NVARCHAR(MAX);
# SET @sql = N'';
# SELECT @sql += 'ALTER TABLE ' + QUOTENAME(s.name) + N'.'
#   + QUOTENAME(t.name) + N' DROP CONSTRAINT '
#   + QUOTENAME(c.name) + ';'
# FROM sys.objects AS c
# INNER JOIN sys.tables AS t
# ON c.parent_object_id = t.[object_id]
# INNER JOIN sys.schemas AS s 
# ON t.[schema_id] = s.[schema_id]
# WHERE c.[type] = 'F'
# ORDER BY c.[type];
# SELECT @sql += 'DROP TABLE ' + QUOTENAME([TABLE_SCHEMA]) + '.' + QUOTENAME([TABLE_NAME]) + ';'
# FROM [INFORMATION_SCHEMA].[TABLES]
# WHERE [TABLE_TYPE] = 'BASE TABLE';
# EXEC SP_EXECUTESQL @sql;""")

        es = self.pm.es
        if es.indices.exists(index=settings.ES_INDEX):
            es.indices.delete(index=settings.ES_INDEX, ignore=400)

        self.pm.cache_client.client.flushall()
