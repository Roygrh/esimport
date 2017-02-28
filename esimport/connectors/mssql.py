import yaml
import pyodbc

from esimport import settings


class MsSQLConnector:

    cfg = None
    conn = None

    def __init__(self):
        if self.cfg is None:
            with open(settings.CONFIG_PATH, 'r') as ymlfile:
                self.cfg = yaml.load(ymlfile)

        args = dict(hostname=self.cfg['ELEVEN_HOST'],
                    database=self.cfg['ELEVEN_DB'],
                    username=self.cfg['ELEVEN_USER'],
                    password=self.cfg['ELEVEN_PASSWORD'])

        self.conn = pyodbc.connect(settings.MSSQL_DSN % args)
        return self.conn.cursor()
