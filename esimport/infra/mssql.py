import logging
from dataclasses import dataclass

import pyodbc

from ._base import BaseInfra


@dataclass
class MsSQLHandler(BaseInfra):

    dsn: str
    database_info: dict

    database_query_timeout: int = 60
    database_connection_timeout: int = 60

    autocommit: bool = True

    default_use_db: str = "Eleven_OS"

    logger: logging.Logger = None

    def __post_init__(self):
        self._log("Setting up MSSQL DB connection")
        self.connect()

    def connect(self):
        self.conn = pyodbc.connect(
            self.dsn % self.database_info,
            autocommit=self.autocommit,
            timeout=self.database_query_timeout,
        )
        self.conn.timeout = self.database_connection_timeout

    def close(self):
        self._log("Closing MSSQL DB connection", level=logging.DEBUG)
        self.conn.close()
        self.conn = None

    def reset(self):
        self._log("Resetting MSSQL DB connection", level=logging.DEBUG)
        self.close()
        self.connect()

    @property
    def cursor(self):
        return self.conn.cursor()

    def execute(self, query, *args):
        # As Eleven uses availability groups, we can't specify db name in DSN string. Rather we have
        # to send an USE command. The API in the pyodbc connector doesn't allow multiple statements
        # in a SQL call. As it remembers context, it's used before every transaction.
        self.cursor.execute(f"USE {self.default_use_db}")
        return self.cursor.execute(query, tuple(args))

    def fetch_rows(self, query, *args, column_names=None):
        for row in self.execute(query, *args):
            if column_names:
                yield dict([(cn, getattr(row, cn, "")) for cn in column_names])
            else:
                yield row

    def fetch_rows_as_dict(self, query, *args):
        rows = self.execute(query, *args)
        column_names = [column[0] for column in rows.description]
        for row in rows:
            if not isinstance(row, dict):
                yield dict([(cn, getattr(row, cn, "")) for cn in column_names])
            else:
                yield row
