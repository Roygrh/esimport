


class BaseModel:

    cursor = None

    def __init__(self, connection):
        self.cursor = connection.cursor


    def fetch(self, query, column_names=None):
        for row in self.cursor.execute(query):
            if column_names:
                yield dict([(cn, getattr(row, cn, '')) for cn in column_names])
            else:
                yield row
