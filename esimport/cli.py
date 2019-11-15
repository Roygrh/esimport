################################################################################
# Copyright 2002-2020 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
import glob
import os
from datetime import datetime

import click
from dotenv import load_dotenv

from .core import SyncBase
from .syncers import (
    AccountsSyncer,
    ConferencesSyncer,
    DeviceSyncer,
    PropertiesSyncer,
    SessionsSyncer,
)

load_dotenv(override=True)
syncer_classes = {
    "accounts": AccountsSyncer,
    "conferences": ConferencesSyncer,
    "devices": DeviceSyncer,
    "properties": PropertiesSyncer,
    "sessions": SessionsSyncer,
}


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "records_type",
    type=click.Choice(
        ["accounts", "conferences", "devices", "properties", "sessions"],
        case_sensitive=False,
    ),
)
@click.option(
    "--start-date",
    default="1900-01-01",
    help="Since when to import data",
    type=click.DateTime(),
)
def sync(records_type: str, start_date: datetime):
    records_type = records_type.lower()
    syncer_class = syncer_classes[records_type]
    syncer = syncer_class()
    syncer.setup()
    syncer.sync(start_date)


@cli.command()
@click.argument("topic_name")
def create_sns_topic(topic_name):
    any_syncer = PropertiesSyncer()
    any_syncer.setup()
    response = any_syncer.aws.create_sns_topic(topic_name)
    click.echo(f"Topic ARN is: {response.arn}")


@cli.command()
@click.argument("table_name")
def create_dynamodb_table(table_name):
    any_syncer = PropertiesSyncer()
    any_syncer.setup()
    response = any_syncer.aws.create_dynamodb_table(table_name)
    click.echo(f"Table is: {response.get('TableDescription').get('TableArn')}")


@cli.command()
def init_dynamodb_table():
    any_syncer = PropertiesSyncer()
    any_syncer.setup()
    now = datetime.utcnow()
    response = any_syncer.put_item_in_dynamodb_table("account", 0, now)
    response = any_syncer.put_item_in_dynamodb_table("device", 0, now)
    response = any_syncer.put_item_in_dynamodb_table("session", 0, now)
    click.echo(f"Table is: {response}")


@cli.command()
def load_fake_data():
    # ensure_db()
    any_syncer = PropertiesSyncer()
    any_syncer.setup()

    test_dir = os.getcwd()

    # for sql in os.listdir(test_dir+'/esimport/tests/fixtures/sql/'):
    #     if '.sql' in sql:
    #         script = test_dir + "/esimport/tests/fixtures/sql/"+sql
    #         subprocess.check_call(["sqlcmd", "-S", host, "-i", script, "-U", uid, "-P", pwd, "-d", db],
    #                                 stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    for sql in glob.glob(os.path.join(test_dir, "/esimport/tests/fixtures/sql/*.sql")):
        with open(sql, "r") as inp:
            sqlQuery = ""
            for line in inp:
                if "GO" not in line:
                    sqlQuery = sqlQuery + line
            _ = any_syncer.mssql.execute(sqlQuery).commit()
            any_syncer.mssql.reset()
        inp.close()

    click.echo("Done!")
