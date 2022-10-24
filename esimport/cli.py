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
import boto3

from .core import SyncBase
from .syncers import (
    AccountsSyncer,
    ConferencesSyncer,
    DeviceSyncer,
    PropertiesSyncer,
    SessionsSyncer,
    DPSKSessionSyncer,
    SessionsCurrentSyncer,
)

here_path = os.path.dirname(__file__)
parent_path = os.path.dirname(here_path)

dotenv_path = os.path.join(parent_path, ".env")

load_dotenv(dotenv_path, override=True)

syncer_classes = {
    "accounts": AccountsSyncer,
    "conferences": ConferencesSyncer,
    "devices": DeviceSyncer,
    "properties": PropertiesSyncer,
    "sessions": SessionsSyncer,
    "sessions_ppk": DPSKSessionSyncer,
    "sessions_current": SessionsCurrentSyncer,
}


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "records_type",
    type=click.Choice(
        [
            "accounts",
            "conferences",
            "devices",
            "properties",
            "sessions",
            "sessions_ppk",
            "sessions_current",
        ],
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
def last_sessions_id():
    syncer_class = syncer_classes["sessions"]
    syncer = syncer_class()
    syncer.setup()
    row = syncer.execute_query(
        "SELECT MAX(ID) as MAX_ID from Radius.dbo.Radius_Accounting_Stop_Event"
    ).fetchone()
    print(row)

@cli.command()
@click.argument("topic_name")
def create_sns_topic(topic_name):
    any_syncer = PropertiesSyncer()
    any_syncer.setup()
    response = any_syncer.aws.create_sns_topic(topic_name)
    click.echo(f"Topic ARN is: {response.arn}")


@cli.command()
@click.argument("topic_name")
@click.argument("kms_key_id")
def create_encrypted_sns_topic(topic_name, kms_key_id):
    any_syncer = PropertiesSyncer()
    any_syncer.setup()
    response = any_syncer.aws.create_encrypted_sns_topic(topic_name, kms_key_id)
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


@cli.command()
@click.argument("source_sqs_queue_arn")
@click.argument("target_sqs_queue_arn")
def replay_dlq_messages(source_sqs_queue_arn: str, target_sqs_queue_arn: str):
    # get queue names from arns which is the last
    source_queue_name = source_sqs_queue_arn.split(":")[-1]
    target_queue_name = target_sqs_queue_arn.split(":")[-1]

    # get account id from arns which is second last
    source_queue_account_id = source_sqs_queue_arn.split(":")[-2]
    target_queue_account_id = target_sqs_queue_arn.split(":")[-2]

    # get region from arns which is third last
    source_queue_region = source_sqs_queue_arn.split(":")[-3]
    target_queue_region = target_sqs_queue_arn.split(":")[-3]

    # construct the queue urls. this might change in future as it is not
    # recommended to construct urls from arn. An issue is open in aws github
    # for a method for this

    source_queue_url = (
        "https://sqs."
        + source_queue_region
        + ".amazonaws.com/"
        + source_queue_account_id
        + "/"
        + source_queue_name
    )

    target_queue_url = (
        "https://sqs."
        + target_queue_region
        + ".amazonaws.com/"
        + target_queue_account_id
        + "/"
        + target_queue_name
    )

    sqs = boto3.resource("sqs")
    source_queue = sqs.Queue(source_queue_url)
    target_queue = sqs.Queue(target_queue_url)

    while True:
        sqs_msgs = source_queue.receive_messages(
            AttributeNames=["All"],
            MessageAttributeNames=["All"],
            WaitTimeSeconds=20,
            MaxNumberOfMessages=1,
        )
        if len(sqs_msgs) != 0:
            target_queue.send_message(MessageBody=sqs_msgs[0].body)
            source_queue.delete_messages(
                Entries=[
                    {
                        "Id": sqs_msgs[0].message_id,
                        "ReceiptHandle": sqs_msgs[0].receipt_handle,
                    }
                ]
            )
        else:
            break
