import sys
import click
import logging

from esimport import settings
from esimport.mappings.account import AccountMapping
from esimport.mappings.property import PropertyMapping


def setup_logging():
    formatter = logging.Formatter(settings.LOG_FORMAT)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(settings.LOG_LEVEL)
    ch.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(settings.LOG_LEVEL)
    logger.addHandler(ch)


@click.group()
def cli():
    setup_logging()


@cli.command()
@click.argument('mapping_name')
@click.option('--start-date', help='Since when to import data (YYYY-MM-DD)')
def sync(mapping_name, start_date):
    mapping_name = mapping_name.lower()
    if mapping_name == 'account':
        am = AccountMapping()
        am.setup_config()
        am.setup_connection()
        try:
            while True:
                am.add_accounts(am.max_id(), start_date)
        except KeyboardInterrupt:
            pass
    elif mapping_name == 'property':
        pm = PropertyMapping()
        pm.sync()


@cli.command()
@click.argument('mapping_name')
def update(mapping_name):
    am = AccountMapping()
    am.setup_config()
    am.setup_connection()
    am.bulk_update(am.get_es_count())
