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

# Are we inside Docker?
INSIDE_DOCKER = os.getenv('INSIDE_DOCKER') in ['1', 'y', 'yes', 'true']

# Wait between database queries execution (seconds)
DATABASE_CALLS_WAIT = 1

# Database timeouts (seconds)
DATABASE_CONNECTION_TIMEOUT = 60
DATABASE_QUERY_TIMEOUT = 60

# TODO: Since we now connect to SQL via the SQL Listener High Availability Group,
# we no longer need to account for any DNS propagation changes.  We should remove this.
# Reset database connection (seconds) giving esimport a chance to
# pickup any DNS changes that have propagated since the last connection
DATABASE_CONNECTION_RESET_LIMIT = 300

DATABASE_CALLS_RETRIES = 10
DATABASE_CALLS_RETRIES_WAIT = 5
DATABASE_CALLS_RETRIES_WAIT_INCREMENTAL = True

# the number of records to return from sql queries where TOP X is used.
DATABASE_RECORD_LIMIT = 10000   

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
#MSSQL_DSN = "Driver={SQL Server};Server=.;Trusted_Connection=yes;"

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

# Datadog
DATADOG_API_KEY = ''
DATADOG_ACCOUNT_METRIC = 'esimport.account.minutes_behind'
DATADOG_CONFERENCE_METRIC = 'esimport.conference.minutes_behind'
DATADOG_DEVICE_METRIC = 'esimport.device.minutes_behind'
DATADOG_PROPERTY_METRIC = 'esimport.property.minutes_behind'
DATADOG_SESSION_METRIC = 'esimport.session.minutes_behind'

from local_settings import *
