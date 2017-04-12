import six
import pprint
import logging

from elasticsearch import Elasticsearch

from esimport import settings
from esimport.models.account import Account
from esimport.connectors.mssql import MsSQLConnector
from esimport.mappings.property import PropertyMapping
from esimport.mappings.base import BaseMapping


logger = logging.getLogger(__name__)


class AccountMapping(BaseMapping):

    step_size = None
    esTimeout = None
    esRetry = None

    cursor = None
    model = None
    es = None



    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=2, depth=10) # pragma: no cover
        self.step_size = settings.ES_BULK_LIMIT
        self.esTimeout = settings.ES_TIMEOUT
        self.esRetry = settings.ES_RETRIES


    # FIXME: move it to connectors module
    def setup(self): # pragma: no cover
        if self.cursor is None:
            logger.debug("Setting up DB connection")
            conn = MsSQLConnector()
            self.cursor = conn.cursor
            self.model = Account(conn)

        if self.es is None:
            logger.debug("Setting up ES connection")
            # defaults to localhost:9200
            self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

        self.pm = PropertyMapping()
        self.pm.setup()


    def add_accounts(self, max_id, start_date='1900-01-01'):
        start = end = max_id + 1
        count = 0
        actions = []
        for account in self.model.get_accounts(start, self.step_size, start_date):
            count += 1
            end = long(account.ID) if six.PY2 else int(account.ID)
            actions.append(account.action)

        if actions:
            if settings.LOG_LEVEL == logging.DEBUG: # pragma: no cover
                for action in actions:
                    logger.debug("Adding Account: {0}".format(self.pp.pformat(action)))

            # add batch of accounts to ElasticSearch
            self.bulk_add_or_update(self.es, actions, self.esRetry, self.esTimeout)
            logger.info("Added {0} entries {1} through {2}" \
                    .format(count, start, end))


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
            accounts.append(account)
            ids.append(str(account.get('ID')))

        q = Account.query_records_by_zpa_id(ids)
        rows = self.cursor.execute(q)
        columns = [column[0] for column in rows.description]
        for row in rows:
            logger.debug("Record found: {0}".format(row))
            es_records = filter(lambda x: x if x.get('ID') == row.ID else [None], accounts)
            if not isinstance(es_records, list):
                es_records = list(es_records)
            if es_records:
                account = (dict(zip(columns, row)), es_records[0])
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
                new_account = Account.make_json(current.get('ID'), new_record)
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
