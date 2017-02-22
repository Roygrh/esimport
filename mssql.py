# ######################################################################################################################
#
# Python2.7 Script: mssql.py
#
# Purpose: ElevenOS->Elastic Search importer.
#
# Author: Sean P. Parker
# Date: October 2016
#
# Copyright @ 2016 Eleven Wireless Inc.
#
# ######################################################################################################################

# DRIVER
import sys
import time
import yaml
import pyodbc
import datetime

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch import exceptions

from esimport.models import Account


reload(sys)
# this is the encoding of our DB
sys.setdefaultencoding('latin1')

cfg = None
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

state = {}
with open(".state.yml", 'r') as ymlfile:
    state = yaml.load(ymlfile)

step_size = state['step_size']
position = state['position']
esTimeout = state['timeout']
esRetry = state['retries']

# Linux
conn = pyodbc.connect("DSN=esimport_local;trusted_connection=no;UID={0};PWD={1}" \
             .format(cfg['ELEVEN_USER'], cfg['ELEVEN_PASSWORD']))

# Windows
# conn = pyodbc.connect("DRIVER={{SQL Server}};SERVER={0}; database={1}; \
#        trusted_connection=no;UID={2};PWD={3}".format(cfg['ELEVEN_HOST'], cfg['ELEVEN_DB'],
#                                                      cfg['ELEVEN_USER'], cfg['ELEVEN_PASSWORD']))

cursor = conn.cursor()

# defaults to localhost:9200
es = Elasticsearch(cfg['ES_HOST'] + ":" + cfg['ES_PORT'])


# find max databaseId
def max_id():
    return cursor.execute("select max(id) from Member").fetchone()


def bulk_add(es, actions, retries, timeout):
    attempts = 0
    while attempts < retries:
        try:
            attempts += 1
            helpers.bulk(es, actions, request_timeout=timeout)
            return
        except exceptions.ConnectionTimeout as err:
            print("ElasticSearch Connection Timeout..")
            logging.warning("{0}: {1}".format(datetime.datetime.now(), err))
            time.sleep(attempts * 5)
        except:
            print("{0}: Unexpected error.. {1}".format(sys.exc_info()[0]))
            logging.warning("{0}: Unexpected error.. {1}".format(sys.exc_info()[0]))
            raise
    raise


def add_accounts(start, end):
    logging.info("Adding Member_ID from {0} to {1}".format(start, end))
    position = start
    while position <= end:
        count = 0
        actions = []
        for row in cursor.execute(Account.eleven_query(position, position + step_size)):
            count += 1
            account = Account(row)
            actions.append(account.action)

        # add batch of accounts to ElasticSearch
        bulk_add(es, actions, esRetry, esTimeout)
        logging.debug(
            "{0}: Added {1} entries {2} through {3}".format(datetime.datetime.now(), count, position,
                                                            position + step_size - 1))
        print("{0}: Added {1} entries {2} through {3}".format(datetime.datetime.now(), count, position,
                                                              position + step_size - 1))
        position += step_size

    logging.info("{0}: Finished account import.".format(datetime.datetime.now()))

# Exe
add_accounts(position, max_id())
