################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import chardet
import datetime
import glob
import os
import threading
import time

from datetime import datetime, timezone
from operator import itemgetter

from esimport import settings, tests
from esimport.connectors.mssql import MsSQLConnector
from esimport.models.conference import Conference
from esimport.mappings.conference import ConferenceMapping
from esimport.models.base import BaseModel
from esimport.models import ESRecord

from elasticsearch import Elasticsearch

from unittest import TestCase
import pytest

class TestConferenceMappingElasticSearch(TestCase):

    def setUp(self):

        test_dir = os.getcwd()
        host = settings.DATABASES['default']['HOST']
        uid = settings.DATABASES['default']['USER']
        pwd = settings.DATABASES['default']['PASSWORD']
        db = settings.DATABASES['default']['NAME']

        self.cm = ConferenceMapping()
        self.cm.setup()

        for sql in glob.glob(test_dir+'/esimport/tests/fixtures/sql/*.sql'):
            with open(sql, 'b+r') as inp:
                sqlQuery = ''
                inp_b = inp.read()
                the_encoding = chardet.detect(inp_b)['encoding']
                inp = inp_b.decode(the_encoding).replace('GO', '')
                self.cm.model.execute(inp)

        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

        # create index
        self.es.indices.create(index=settings.ES_INDEX, ignore=400)

    @pytest.mark.xfail(strict=True)
    def test_conference_update_in_elasticsearch(self):
        # cm.update() method make sql request that return records with column ServiceArea that always = Null
        # so this test is broken and can't be fixed without changing fixutres or core code
        cm = ConferenceMapping()
        cm.setup()
        cm.update('2018-05-01')

        conference_list = []
        confs = [conf for conf in self.cm.model.get_conferences(0, 5, '2018-05-01')]
        for conf in confs:
            conference_list.append(conf.record)
        conference_list.sort(key=itemgetter('ID'))

        # get all property from elasticsearch
        conference_es_list = []
        query = {'query': {'term': {'_type': 'conference'}}}
        conference_es = self.es.search(index=settings.ES_INDEX, body=query)['hits']['hits']
        for conf in conference_es:
            conference_es_list.append(conf['_source'])
        conference_es_list.sort(key=itemgetter('ID'))

        for i in range(0,len(conference_list)):
            for key in conference_list[i].items():

                if key[0] == 'UpdateTime':
                    continue
                if key[0] == 'EndDateUTC' or key[0] == 'DateCreatedUTC' or key[0] == 'StartDateUTC':
                    conference_es_list[i][key[0]] = datetime.strptime(conference_es_list[i][key[0]], '%Y-%m-%dT%H:%M:%S.%f+00:00').replace(tzinfo=timezone.utc)

                self.assertEqual(conference_list[i][key[0]], conference_es_list[i][key[0]])


    def test_conference_data_has_access_codes_nested_objects(self):
        cm = ConferenceMapping()
        cm.setup()

        conference_update = lambda _cm: _cm.update('2018-05-01')
        t = threading.Thread(target=conference_update, args=(cm,), daemon=True)
        t.start()

        # time to catch up
        time.sleep(5)

       # get all property from elasticsearch
        conference_es_list = []
        query = {'query': {'term': {'_type': 'conference'}}}
        conference_es = self.es.search(index=settings.ES_INDEX, body=query)['hits']['hits']
        for conference in conference_es:
            conference_data = conference['_source']
            # Make sure AccessCodes exists
            # and is a list of at least one element
            access_codes = conference_data.get('AccessCodes')
            assert access_codes and isinstance(access_codes, list)
            assert len(access_codes) >= 1
            # Make sure it contains Code, MemberNumber and MemberID
            should_contain = ['Code', 'MemberNumber', 'MemberID']
            for key in access_codes[0].keys():
                assert key in should_contain


    def test_conference_data_has_group_bandwidth_limit(self):
        cm = ConferenceMapping()
        cm.setup()

        conference_update = lambda _cm: _cm.update('2018-05-01')
        t = threading.Thread(target=conference_update, args=(cm,), daemon=True)
        t.start()
        # time to catch up
        time.sleep(5)

       # get all conferences from elasticsearch
        conference_es_list = []
        query = {'query': {'term': {'_type': 'conference'}}}
        conference_es = self.es.search(index=settings.ES_INDEX, body=query)['hits']['hits']
        for conference in conference_es:
            conference_data = conference['_source']
            # make sure GroupBandwidthLimit exists and is type of bool:
            group_bandwidth_limit = conference_data.get('GroupBandwidthLimit')
            assert isinstance(group_bandwidth_limit, bool)


    def tearDown(self):
        self.cm.model.execute("""
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

        es = self.cm.es
        if es.indices.exists(index=settings.ES_INDEX):
            es.indices.delete(index=settings.ES_INDEX, ignore=400)
