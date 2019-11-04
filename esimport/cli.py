################################################################################
# Copyright 2002-2020 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
from datetime import datetime

import click

from .syncers import (
    AccountsSyncer,
    ConferencesSyncer,
    DeviceSyncer,
    PropertiesSyncer,
    SessionsSyncer,
)

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

