import sys
import time
import yaml
import pyodbc
import pprint
import logging
import traceback

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch import exceptions

from esimport.models import Account


logger = logging.getLogger(__name__)


class AccountMapping:

    cfg = None

    step_size = None
    position = None
    esTimeout = None
    esRetry = None

    conn = None
    cursor = None
    es = None


    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=2, depth=10)


    def setup_config(self):
        if self.cfg is None:
            with open("config.yml", 'r') as ymlfile:
                self.cfg = yaml.load(ymlfile)

        state = {}
        with open(".state.yml", 'r') as ymlfile:
            state = yaml.load(ymlfile)

        self.step_size = state['step_size']
        self.position = state['position']
        self.esTimeout = state['timeout']
        self.esRetry = state['retries']


    def setup_connection(self):
        if self.conn is None:
            # Linux
            self.conn = pyodbc.connect("DSN=esimport_local;trusted_connection=no;UID={0};PWD={1}" \
                         .format(self.cfg['ELEVEN_USER'], self.cfg['ELEVEN_PASSWORD']))

            # Windows
            # self.conn = pyodbc.connect("DRIVER={{SQL Server}};SERVER={0}; database={1}; \
            #        trusted_connection=no;UID={2};PWD={3}".format(self.cfg['ELEVEN_HOST'], self.cfg['ELEVEN_DB'],
            #                                                      self.cfg['ELEVEN_USER'], self.cfg['ELEVEN_PASSWORD']))

        if self.conn and self.cursor is None:
            self.cursor = self.conn.cursor()

        if self.es is None:
            # defaults to localhost:9200
            self.es = Elasticsearch(self.cfg['ES_HOST'] + ":" + self.cfg['ES_PORT'])


    # find max databaseId
    def max_id(self):
        result = self.cursor.execute("SELECT MAX(id) FROM Member").fetchone()
        if result:
            return int(result[0])
        return 0


    def bulk_add(self, es, actions, retries, timeout):
        attempts = 0
        while attempts < retries:
            try:
                attempts += 1
                helpers.bulk(es, actions, request_timeout=timeout)
                return
            except exceptions.ConnectionTimeout as err:
                logger.error(err)
                traceback.print_exc(file=sys.stdout)
                time.sleep(attempts * 5)
            except Exception as err:
                logger.error(err)
                traceback.print_exc(file=sys.stdout)

    def get_accounts(self, start, end):
        logger.debug("Searching by Member.ID from {0} to {1}".format(start, end))
        q = Account.eleven_query(start, end)
        for row in self.cursor.execute(q):
            logger.debug("Record found: {0}".format(row))
            yield Account(row)

    def add_accounts(self, max_id):
        while self.position <= max_id:
            count = 0
            actions = []
            end = min(self.position + self.step_size, max_id)
            for account in self.get_accounts(self.position, end):
                count += 1
                actions.append(account.action)

            if actions:
                for action in actions:
                    logger.debug("Adding Account: {0}".format(self.pp.pformat(action)))

                # add batch of accounts to ElasticSearch
                self.bulk_add(self.es, actions, self.esRetry, self.esTimeout)
                logger.info("Added {0} entries {1} through {2}" \
                        .format(count, self.position, self.position + self.step_size - 1))

            self.position += self.step_size

        logger.info("Finished account import")
