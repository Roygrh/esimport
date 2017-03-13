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


    def bulk_add(self, es, actions, retries, timeout):
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
        while True:
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
                self.bulk_add(self.es, actions, self.esRetry, self.esTimeout)
                logger.info("Added {0} entries {1} through {2}" \
                        .format(count, start, end))
