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
import click
import pyodbc
import traceback

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch import exceptions

from esimport.models import Account
from esimport.log import logger


cfg = None
state = None

step_size = None
position = None
esTimeout = None
esRetry = None

conn = None
cursor = None
es = None


def setup_config():
    if cfg is None:
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

    if state is None:
        with open(".state.yml", 'r') as ymlfile:
            state = yaml.load(ymlfile)

    step_size = state['step_size']
    position = state['position']
    esTimeout = state['timeout']
    esRetry = state['retries']


def setup_connection():
    if conn is None:
        # Linux
        conn = pyodbc.connect("DSN=esimport_local;trusted_connection=no;UID={0};PWD={1}" \
                     .format(cfg['ELEVEN_USER'], cfg['ELEVEN_PASSWORD']))

        # Windows
        # conn = pyodbc.connect("DRIVER={{SQL Server}};SERVER={0}; database={1}; \
        #        trusted_connection=no;UID={2};PWD={3}".format(cfg['ELEVEN_HOST'], cfg['ELEVEN_DB'],
        #                                                      cfg['ELEVEN_USER'], cfg['ELEVEN_PASSWORD']))

    if conn and cursor is None:
        cursor = conn.cursor()

    if es is None:
        # defaults to localhost:9200
        es = Elasticsearch(cfg['ES_HOST'] + ":" + cfg['ES_PORT'])


# find max databaseId
def max_id():
    result = cursor.execute("SELECT MAX(id) FROM Member").fetchone()
    if result:
        return int(result[0])
    return 0


def bulk_add(es, actions, retries, timeout):
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


def add_accounts(start, end):
    logger.info("Adding Member_ID from {0} to {1}".format(start, end))
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
        logger.debug("Added {0} entries {1} through {2}" \
                .format(count, position, position + step_size - 1))
        position += step_size

    logger.info("Finished account import")


@click.command()
def cli():
    add_accounts(position, max_id())
