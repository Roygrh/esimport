import time
import pyodbc
import logging

from esimport import settings


logger = logging.getLogger(__name__)


class BaseModel(object):

    conn = None

    def __init__(self, connection):
        self.conn = connection


    def execute(self, query,
                retry=settings.DATABASE_CALLS_RETRIES,
                retry_wait=settings.DATABASE_CALLS_RETRIES_WAIT):
        result = None
        try:
            result = self.conn.cursor.execute(query)
        except pyodbc.Error as err:
            logger.error(err)
            if retry > 0:
                retry -= 1
                logger.info('Retry {0} of {1} in {2} seconds'
                      .format((settings.DATABASE_CALLS_RETRIES - retry), settings.DATABASE_CALLS_RETRIES,
                                retry_wait))
                time.sleep(retry_wait)
                if settings.DATABASE_CALLS_RETRIES_WAIT_INCREMENTAL:
                    retry_wait += settings.DATABASE_CALLS_RETRIES_WAIT
                result = self.execute(query, retry=retry, retry_wait=retry_wait)
            else:
                raise err
        return result


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
