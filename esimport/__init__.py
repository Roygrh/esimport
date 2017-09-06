import sys
import click
import logging

from esimport import settings
from esimport.mappings.account import AccountMapping
from esimport.mappings.session import SessionMapping
from esimport.mappings.property import PropertyMapping
from esimport.mappings.init_index import new_index
from esimport.mappings.device import DeviceMapping
from esimport.mappings.conference import ConferenceMapping



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
@click.option('--start-date', default='1900-01-01', help='Since when to import data (YYYY-MM-DD)')
def sync(mapping_name, start_date):
    mapping_name = mapping_name.lower()
    if mapping_name == 'account':
        am = AccountMapping()
        am.setup()
        am.sync(start_date)
    elif mapping_name == 'session':
        sm = SessionMapping()
        sm.setup()
        sm.sync(start_date)
    elif mapping_name == 'property':
        pm = PropertyMapping()
        pm.setup()
        pm.sync()
    elif mapping_name == 'device':
        dm = DeviceMapping()
        dm.setup()
        dm.sync(start_date)
    elif mapping_name == 'conference':
        cm = ConferenceMapping()
        cm.setup()
        cm.sync(start_date)


@cli.command()
@click.argument('mapping_name')
@click.option('--start-date', default='1900-01-01', help='Since when to import data (YYYY-MM-DD)')
def backload(mapping_name, start_date):
    mapping_name = mapping_name.lower()
    if mapping_name == 'account':
        am = AccountMapping()
        am.setup()
        am.backload(start_date)
    elif mapping_name == 'session':
        pm = SessionMapping()
        pm.setup()
        pm.backload(start_date)


@cli.command()
@click.argument('mapping_name')
@click.option('--start-date', default='1900-01-01', help='Since when to import data (YYYY-MM-DD)')
def update(mapping_name, start_date):
    mapping_name = mapping_name.lower()
    if mapping_name == 'property':
        pm = PropertyMapping()
        pm.setup()
        pm.update()
    if mapping_name == 'conference':
        cm = ConferenceMapping()
        cm.setup()
        cm.update(start_date)

@cli.command()
def create():
        ni = new_index()
        ni.setup()
        ni.setupindex()
