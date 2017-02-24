import sys
import logging

import settings


@property
def logger(name):
    formatter = logging.Formatter(settings.LOG_FORMAT)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(settings.LOG_LEVEL)
    ch.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    logger.addHandler(ch)
    return logger
