import csv

from datetime import datetime

from esimport import settings


class Records(list):

    _keys = []

    def __init__(self, *args, **kwargs):
        self._keys = kwargs.get('keys')
        super(Records, self).__init__(args)


    def setKeys(self, keys=[]):
        self._keys = keys


    @property
    def description(self):
        return self._keys


def _mocked_sql(filename='multiple_orders.csv'):
    dt_format = '%Y-%m-%d %H:%M:%S.%f'

    records = Records()
    with open('{0}/{1}'.format(settings.TEST_FIXTURES_DIR, filename)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            records.setKeys(row.keys())
            records.append(row)
    return records
