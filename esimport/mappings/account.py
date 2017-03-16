import sys
import time
import yaml
import pprint
import logging
import traceback

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch import exceptions

from esimport import settings
from esimport.models import Account
from esimport.connectors.mssql import MsSQLConnector


logger = logging.getLogger(__name__)


class AccountMapping:

    cfg = None

    step_size = None
    esTimeout = None
    esRetry = None

    cursor = None
    es = None


    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=2, depth=10) # pragma: no cover


    def setup_config(self):
        if self.cfg is None:
            with open(settings.CONFIG_PATH, 'r') as ymlfile:
                self.cfg = yaml.load(ymlfile)

        self.step_size = self.cfg['ES_BULK_LIMIT']
        self.esTimeout = self.cfg['ES_TIMEOUT']
        self.esRetry = self.cfg['ES_RETRIES']


    # FIXME: move it to connectors module
    def setup_connection(self): # pragma: no cover
        if self.cursor is None:
            self.cursor = MsSQLConnector().cursor

        if self.es is None:
            # defaults to localhost:9200
            self.es = Elasticsearch(self.cfg['ES_HOST'] + ":" + self.cfg['ES_PORT'])


    # find max Zone_Plan_Account.ID from ElasticSearch
    def max_id(self):
        filters = dict(index=Account.get_index(), doc_type=Account.get_type(),
                        body={
                            "aggs": {
                                "max_id": {
                                  "max": {
                                    "field": "ID"
                                  }
                                }
                              },
                              "size": 0
                            })
        response = self.es.search(**filters)
        try:
            _id = response['aggregations']['max_id']['value']
            if _id:
                return int(_id)
        except Exception as err:
            logger.error(err)
            traceback.print_exc(file=sys.stdout)
        return 0


    def bulk_add_or_update(self, es, actions, retries, timeout):
        attempts = 0
        while attempts < retries:
            try:
                attempts += 1
                helpers.bulk(es, actions, request_timeout=timeout)
                break
            except exceptions.ConnectionTimeout as err:
                logger.error(err)
                traceback.print_exc(file=sys.stdout)
                time.sleep(attempts * 5) # pragma: no cover
            except Exception as err:
                logger.error(err)
                traceback.print_exc(file=sys.stdout)
        return attempts

    def get_accounts(self, start, end):
        logger.debug("Searching by Zone_Plan_Account.ID from {0} to {1}".format(start, end))
        q = Account.eleven_query(start, end)
        for row in self.cursor.execute(q):
            logger.debug("Record found: {0}".format(row))
            yield Account(row)

    def add_accounts(self, max_id):
        start = end = max_id
        count = 0
        actions = []
        start = end
        end = start + self.step_size
        for account in self.get_accounts(start, end):
            count += 1
            actions.append(account.action)

        if actions:
            if settings.LOG_LEVEL == logging.DEBUG: # pragma: no cover
                for action in actions:
                    logger.debug("Adding Account: {0}".format(self.pp.pformat(action)))

            # add batch of accounts to ElasticSearch
            self.bulk_add_or_update(self.es, actions, self.esRetry, self.esTimeout)
            logger.info("Added {0} entries {1} through {2}" \
                    .format(count, start, end))


    def get_es_count(self):
        filters = dict(index=Account.get_index(), doc_type=Account.get_type())
        response = self.es.count(**filters)
        try:
            return response['count']
        except Exception as err:
            logger.error(err)
            traceback.print_exc(file=sys.stdout)
        return 0


    """
    Get existing accounts from ElasticSearch
    """
    def get_existing_accounts(self, start_zpa_id, limit):
        logger.debug("Fetching {0} records from ES where ID >= {1}" \
                .format(limit, start_zpa_id))
        records = self.es.search(index=Account.get_index(), doc_type=Account.get_type(),
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
