import sys
import time
import yaml
import pyodbc
import traceback

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch import exceptions

from esimport.models import Account
from esimport.log import logger


class AccountMapping:

    cfg = None

    step_size = None
    position = None
    esTimeout = None
    esRetry = None

    conn = None
    cursor = None
    es = None

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


    def add_accounts(self, end):
        start = self.position
        logger.info("Adding Member_ID from {0} to {1}".format(start, end))
        while self.position <= end:
            count = 0
            actions = []
            for row in self.cursor.execute(Account.eleven_query(self.position, self.position + self.step_size)):
                count += 1
                account = Account(row)
                logger.debug("Adding record {0}".format(row))
                actions.append(account.action)

            # add batch of accounts to ElasticSearch
            self.bulk_add(self.es, actions, self.esRetry, self.esTimeout)
            logger.debug("Added {0} entries {1} through {2}" \
                    .format(count, self.position, self.position + self.step_size - 1))
            self.position += self.step_size

        logger.info("Finished account import")
