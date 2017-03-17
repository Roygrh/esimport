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
# MSSQL_DSN = """DRIVER={{SQL Server}};
# SERVER=%(HOST)s;
# database=%(NAME)s;
# UID=%(USER)s;
# PWD=%(PASSWORD)s;
# trusted_connection=no"""


try:
    from local_settings import *
except:
    pass
