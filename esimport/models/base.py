import time
import pyodbc
import logging

from esimport import settings
from esimport.utils import retry


logger = logging.getLogger(__name__)


class BaseModel(object):

    conn = None

    def __init__(self, connection):
        self.conn = connection


    @retry(settings.DATABASE_CALLS_RETRIES, settings.DATABASE_CALLS_RETRIES_WAIT,
            retry_exception=pyodbc.Error)
    def execute(self, query):
        return self.conn.cursor.execute(query)


    def fetch(self, query, column_names=None):
        for row in self.execute(query):
            if column_names:
                yield dict([(cn, getattr(row, cn, '')) for cn in column_names])
            else:
                yield row


    def fetch_dict(self, query):
        rows = self.execute(query)
        column_names = [column[0] for column in rows.description]
        for row in rows:
            if not isinstance(row, dict):
                yield dict([(cn, getattr(row, cn, '')) for cn in column_names])
            else:
                yield row
