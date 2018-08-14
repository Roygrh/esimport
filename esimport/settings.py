################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import os
import logging


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(PKG_DIR, '..'))

TEST_FIXTURES_DIR = os.path.join(PKG_DIR, 'tests/fixtures')

ES_HOST = 'localhost'
ES_PORT = '9200'
ES_TIMEOUT = 30
ES_RETRIES = 5
ES_RETRIES_WAIT = 5
ES_BULK_LIMIT = 10

# Wait between database queries execution (seconds)
DATABASE_CALLS_WAIT = 1

DATABASE_CALLS_RETRIES = 10
DATABASE_CALLS_RETRIES_WAIT = 5
DATABASE_CALLS_RETRIES_WAIT_INCREMENTAL = True

DATABASE_RECORD_LIMIT = 10000   # the number of records to return from sql queries where TOP X is used.

DATABASES = {
    'default': {
        'DSN': None, # either DSN or HOST
        'HOST': 'localhost',
        'PORT': '1433',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
    }
}

# *nix
MSSQL_DSN = "DSN=%(DSN)s;UID=%(USER)s;PWD=%(PASSWORD)s;trusted_connection=no"

# Windows
#MSSQL_DSN = "Driver={SQL Server};Server=.;Database=Eleven_OS;Trusted_Connection=yes;"

ES_CALLS_RETRIES = 10
ES_CALLS_RETRIES_WAIT = 5
ES_CALLS_RETRIES_WAIT_INCREMENTAL = True

# Sentry
SENTRY_DSN = ''
ES_CLUSTER = ''
SQL_SERVER = ''

# Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# HC Ping URL
ACCOUNT_MAPPING_PING = ''
SESSION_MAPPING_PING = ''
PROPERTY_MAPPING_PING = ''
DEVICE_MAPPING_PING = ''
CONFERENCE_MAPPING_PING = ''


try:
    from local_settings import *
except:
    raise
