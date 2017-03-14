import sys
import click
import logging

from esimport import settings
from esimport.mappings.account import AccountMapping


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
def sync():
    am = AccountMapping()
    am.setup_config()
    am.setup_connection()
    am.add_accounts(am.max_id())


@cli.command()
@click.argument('mapping_name')
def update(mapping_name):
    am = AccountMapping()
    am.setup_config()
    am.setup_connection()
    am.bulk_update(am.get_es_count())
