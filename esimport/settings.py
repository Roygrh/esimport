import os
import logging


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


PKG_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(PKG_DIR, '..'))

DEFAULT_CONFIG_PATH = os.path.join(ROOT_DIR, 'config.yml')
CONFIG_PATH = os.getenv('ESIMPORT_CONFIG', DEFAULT_CONFIG_PATH)

TEST_FIXTURES_DIR = os.path.join(PKG_DIR, 'tests/fixtures')

# *nix
MSSQL_DSN = "DSN=%(dsn)s;UID=%(username)s;PWD=%(password)s;trusted_connection=no"

# Windows
# MSSQL_DSN = """DRIVER={{SQL Server}};
# SERVER=%(hostname)s;
# database=%(database)s;
# UID=%(username)s;
# PWD=%(password)s;
# trusted_connection=no"""
