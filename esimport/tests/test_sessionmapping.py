import os
import glob
import threading
import time
from unittest import TestCase
from elasticsearch import Elasticsearch

from esimport.mappings.session import SessionMapping
from esimport import settings


class TestSessionMappingElasticsearch(TestCase):

    def setUp(self):
        test_dir = os.getcwd()
        host = settings.DATABASES['default']['HOST']
        uid = settings.DATABASES['default']['USER']
        pwd = settings.DATABASES['default']['PASSWORD']
        db = settings.DATABASES['default']['NAME']
        

        self.sm = SessionMapping()
        self.sm.setup()

        for sql in glob.glob(test_dir+'/esimport/tests/fixtures/sql/*.sql'):
            with open(sql, 'r') as inp:
                sqlQuery = ''
                for line in inp:
                    if 'GO' not in line:
                        sqlQuery = sqlQuery + line
                self.sm.model.execute(sqlQuery).commit()
            inp.close()
            self.sm.model.conn.reset()

        # self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)
        self.es = self.sm.es

    def test_session_data_in_es(self):
        self.es.indices.create(index=settings.ES_INDEX)
        sm = SessionMapping()
        sm.setup()
        sync = lambda _sm: _sm.sync('2018-06-27')
        t = threading.Thread(target=sync, args=(sm,), daemon=True)
        t.start()
        time.sleep(2)
        # increase pagination size to 12 as there's 12 rows of session in db
        q = {
                "size": 12,
                "query": {"term": {"_type": "session"}}
        }
        res = self.es.search(index=settings.ES_INDEX, body=q)['hits']['hits']
        session_id_es = [session['_source']['ID'] for session in res]
        session_id_es.sort()
        s = self.sm.model.execute('''SELECT ID FROM Radius.dbo.Radius_Stop_Event''').fetchall()
        stop_ids = [stop_id[0] for stop_id in s]
        stop_ids.sort()
        self.assertEqual(session_id_es, stop_ids)

    def tearDown(self):
        self.sm.model.execute("""
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
EXEC SP_EXECUTESQL @sql;""").commit()

        if self.es.indices.exists(index=settings.ES_INDEX):
            self.es.indices.delete(index=settings.ES_INDEX, ignore=400)
