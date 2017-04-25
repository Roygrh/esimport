import six
import time
import pprint
import logging

from elasticsearch import Elasticsearch

from esimport import settings
from esimport.models import ESRecord
from esimport.models.account import Account
from esimport.connectors.mssql import MsSQLConnector
from esimport.mappings.base import BaseMapping
from esimport.mappings.property import PropertyMapping


logger = logging.getLogger(__name__)


class AccountMapping(BaseMapping):

    step_size = None
    esTimeout = None
    esRetry = None

    model = None
    es = None

    pm = None
    property_fields_include = (
        'PropertyName', 'PropertyNumber',
        'Provider_Display_Name', 'Brand',
        'MARSHA_Code', 'Country', 'Region',
        'SubRegion', 'OwnershipGroup',
        'TaxRate', 'CorporateBrand',
        'ExtPropId',)


    def __init__(self):
        super(AccountMapping, self).__init__()
        self.pp = pprint.PrettyPrinter(indent=2, depth=10) # pragma: no cover
        self.step_size = settings.ES_BULK_LIMIT
        self.esTimeout = settings.ES_TIMEOUT
        self.esRetry = settings.ES_RETRIES
        self.db_wait = settings.DATABASE_CALLS_WAIT


    # FIXME: move it to connectors module
    def setup(self): # pragma: no cover
        logger.debug("Setting up DB connection")
        conn = MsSQLConnector()
        self.model = Account(conn)

        # ARRET! possible cycle calls in future
        self.pm = PropertyMapping()
        self.pm.setup()

        logger.debug("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)


    # Need this for tests
    def add_accounts(self, start_date='1900-01-01'):
        count = 0
        start = self.max_id() + 1
        for account in self.model.get_accounts(start, self.step_size, start_date):
            count += 1

            # get some properties from PropertyMapping
            _action = {}
            for properte in self.pm.get_properties_by_service_area(account.get('ServiceArea')):
                for pfi in self.property_fields_include:
                    _action[pfi] = properte.get(pfi, "")
                break
            account.update(_action)

            rec = account.es()
            logger.debug("Record found: {0}".format(self.pp.pformat(rec)))
            self.add(rec, self.step_size)

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))

        # only wait between DB calls when there is no delay from ES (HTTP requests)
        if count <= 0:
            logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
            time.sleep(self.db_wait)


    def sync(self, start_date):
        while True:
            self.add_accounts(start_date)


    """
    Get existing accounts from ElasticSearch
    """
    def get_existing_accounts(self, start_zpa_id, limit):
        logger.debug("Fetching {0} records from ES where ID >= {1}" \
                .format(limit, start_zpa_id))
        records = self.es.search(index=settings.ES_INDEX, doc_type=Account.get_type(),
                                 sort="ID:asc", size=limit,
                                 q="ID:[{0} TO *]".format(start_zpa_id))
        for record in records['hits']['hits']:
            yield record.get('_source')


    """
    Get records from MSSQL based on records from ElasticSearch
    """
    def get_new_and_existing_accounts_tuples(self, start, limit):
        ids = []
        accounts = []
        for account in self.get_existing_accounts(start, limit):
            # only for account where there are 1 or more missing property fields
            if any([pfi not in account for pfi in self.property_fields_include]):
                new_property_fields_include = [pfi for pfi in self.property_fields_include if pfi not in account]
                # get some properties from PropertyMapping
                _action = {}
                for properte in self.pm.get_properties_by_service_area(account.get('ServiceArea')):
                    for pfi in new_property_fields_include:
                        _action[pfi] = properte.get(pfi, "")
                    break
                account.update(_action)

            accounts.append(account)
            ids.append(str(account.get('ID')))

        for row in self.model.get_records_by_zpa_id(ids):
            logger.debug("Record found: {0}".format(row))
            es_records = filter(lambda x: x if x.get('ID') == row.get('ID') else [None], accounts)
            if not isinstance(es_records, list):
                es_records = list(es_records)
            if es_records:
                account = (row, es_records[0])
                yield account


    """
    Filter records based on new fields found in MSSQL but not in ElasticSearch
    """
    def get_updated_records(self, start, limit):
        ignore_fields = ['Price', 'Currency']

        for new, current in self.get_new_and_existing_accounts_tuples(start, limit):
            new_fields = set(new.keys()) - set(current.keys()) - set(ignore_fields)
            new_record = dict([(k, v) for k,v in new.items() if k in new_fields])
            if len(new_record) > 0:
                new_account = ESRecord(new_record, Account.get_type()) \
                                    .es(record_id=new.get('ID'))
                yield new_account


    def bulk_update(self, total):
        start = 0
        limit = min(self.step_size, total)
        end = start + limit

        while start < total:
            actions = list(self.get_updated_records(start, limit))
            if settings.LOG_LEVEL == logging.DEBUG: # pragma: no cover
                if actions:
                    for action in actions:
                        logger.debug("Updating Account: {0}".format(self.pp.pformat(action)))
            self.bulk_add_or_update(self.es, actions, self.esRetry, self.esTimeout)

            start = end + 1
            end = min(start + limit, total)


    def backload(self, start_date):
        start = 0
        for account in self.model.get_accounts(start, self.step_size, start_date):
            acc = account.es()
            logger.debug("Record found: {0}".format(self.pp.pformat(acc)))
            self.add(dict(acc), self.step_size)
            start = account.get('ID') + 1

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))
