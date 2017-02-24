import os
import logging


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


PKG_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(PKG_DIR, '..'))

CONFIG_PATH = os.path.join(ROOT_DIR, 'config.yml')
STATE_PATH = os.path.join(ROOT_DIR, '.state.yml')
