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


def _mocked_sql():
    dt_format = '%Y-%m-%d %H:%M:%S.%f'

    records = Records()
    with open('{0}/multiple_orders.csv'.format(settings.TEST_FIXTURES_DIR)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            records.setKeys(row.keys())
            row['Created'] = datetime.strptime(row.get('Created'), dt_format)
            row['Activated'] = datetime.strptime(row.get('Activated'), dt_format)
            records.append(row)
    return records
