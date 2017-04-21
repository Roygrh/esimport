import logging


logger = logging.getLogger(__name__)


class BaseModel(object):

    cursor = None

    def __init__(self, connection):
        self.cursor = connection.cursor


    def fetch(self, query, column_names=None):
        for row in self.cursor.execute(query):
            if column_names:
                yield dict([(cn, getattr(row, cn, '')) for cn in column_names])
            else:
                yield row


    def fetch_dict(self, query):
        rows = self.cursor.execute(query)
        column_names = [column[0] for column in rows.description]
        for row in rows:
            if not isinstance(row, dict):
                yield dict([(cn, getattr(row, cn, '')) for cn in column_names])
            else:
                yield row
