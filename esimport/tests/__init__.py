import csv

from datetime import datetime
from collections import namedtuple

from esimport import settings


def _mocked_sql():
        dt_format = '%Y-%m-%d %H:%M:%S.%f'

        rows = []
        with open('{0}/multiple_orders.csv'.format(settings.TEST_FIXTURES_DIR)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_tuple = namedtuple('GenericDict', row.keys())(**row)
                row_tuple = row_tuple._replace(Created=datetime.strptime(row_tuple.Created, dt_format))
                row_tuple = row_tuple._replace(Activated=datetime.strptime(row_tuple.Activated, dt_format))
                rows.append(row_tuple)
        return rows
