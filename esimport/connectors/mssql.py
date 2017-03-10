import yaml
import pyodbc

from esimport import settings


class MsSQLConnector:

    cfg = None
    conn = None

    _cursor = None


    def __init__(self):
        if self.cfg is None:
            with open(settings.CONFIG_PATH, 'r') as ymlfile:
                self.cfg = yaml.load(ymlfile)

        args = dict(dsn=self.cfg.get('ELEVEN_DSN'),
                    hostname=self.cfg.get('ELEVEN_HOST'),
                    database=self.cfg['ELEVEN_DB'],
                    username=self.cfg['ELEVEN_USER'],
                    password=self.cfg['ELEVEN_PASSWORD'])

        self.conn = pyodbc.connect(settings.MSSQL_DSN % args)


    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self.conn.cursor()
        return self._cursor
