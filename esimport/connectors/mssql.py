import pyodbc

from esimport import settings

import logging
logger = logging.getLogger(__name__)


class MsSQLConnector:

    cfg = None
    conn = None

    def __init__(self):
        logger.info("Setting up DB connection")
        db = settings.DATABASES.get('default', {})
        self.conn = pyodbc.connect(
            settings.MSSQL_DSN % db, 
            autocommit=True,
            timeout=settings.DATABASE_QUERY_TIMEOUT)
        self.conn.timeout = settings.DATABASE_CONNECTION_TIMEOUT

    def reset(self):
        self.conn.close()
        del self.conn
        db = settings.DATABASES.get('default', {})
        self.conn = pyodbc.connect(
            settings.MSSQL_DSN % db, 
            autocommit=True,
            timeout=settings.DATABASE_QUERY_TIMEOUT)
        self.conn.timeout = settings.DATABASE_CONNECTION_TIMEOUT

    @property
    def cursor(self):
        return self.conn.cursor()
