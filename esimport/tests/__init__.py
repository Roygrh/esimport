import csv

from datetime import datetime
from collections import namedtuple

from esimport import settings


class Records(list):

    _keys = []

    def __init__(self, *args, **kwargs):
        self._keys = kwargs.get('keys')
        super(Records, self).__init__(args)

    @property
    def description(self):
        return self._keys


def _mocked_sql():
        dt_format = '%Y-%m-%d %H:%M:%S.%f'

        records = None
        with open('{0}/multiple_orders.csv'.format(settings.TEST_FIXTURES_DIR)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                column_names = row.keys()
                if records is None:
                    records = Records(keys=column_names)
                row_tuple = namedtuple('GenericDict', column_names)(**row)
                row_tuple = row_tuple._replace(Created=datetime.strptime(row_tuple.Created, dt_format))
                row_tuple = row_tuple._replace(Activated=datetime.strptime(row_tuple.Activated, dt_format))
                records.append(row_tuple)
        return records
