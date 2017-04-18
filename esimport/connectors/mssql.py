import pyodbc

from esimport import settings

import logging
logger = logging.getLogger(__name__)


class MsSQLConnector:

    cfg = None
    conn = None

    _cursor = None


    def __init__(self):
        db = settings.DATABASES.get('default', {})
        self.conn = pyodbc.connect(settings.MSSQL_DSN % db)


    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self.conn.cursor()
        return self._cursor
