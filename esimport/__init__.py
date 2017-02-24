import click

from esimport.mappings.account import AccountMapping


@click.group()
def cli():
    pass


@cli.command()
@click.argument('mapping_name')
def update(mapping_name):
    am = AccountMapping()
    am.setup_config()
    am.setup_connection()
    am.add_accounts(am.max_id())
