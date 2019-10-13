import argparse
import logging
import sys
from os import environ

from esimport_retention_core import delete_snapshot
from esimport_retention_core import get_awsauth
from esimport_retention_core import get_repo_definition
from esimport_retention_core import get_repo_info
from esimport_retention_core import get_signed_es
from esimport_retention_core import get_snapshot_body
from esimport_retention_core import is_snapshot_ok
from esimport_retention_core import parse_es_url
from esimport_retention_core import put_test_document
from esimport_retention_core import register_snapshot_repo
from esimport_retention_core import take_snapshot

FORMAT = "%(asctime)-15s %(filename)s %(lineno)d %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)

try:
    _log_level = environ.get("LOG_LEVEL")
    LOG_LEVEL = logging.getLevelName(_log_level)
    logger.setLevel(LOG_LEVEL)
except ValueError as _err:
    logger.setLevel(logging.DEBUG)


def cli_entrypoint(input_args):
    if input_args.subcommand == "register_new":
        (region, host) = parse_es_url(input_args.es_url)
        s3_bucket_name, s3_region = input_args.s3_bucket
        awsauth = get_awsauth(region)
        es = get_signed_es(host, awsauth)

        repo_definition = get_repo_definition(s3_bucket_name, s3_region, input_args.arn)
        register_snapshot_repo(es, input_args.repo_name, repo_definition)

    elif input_args.subcommand == "repo_info":
        (region, host) = parse_es_url(input_args.es_url)
        awsauth = get_awsauth(region)
        es = get_signed_es(host, awsauth)

        repo_info = get_repo_info(es, input_args.repo_name)
        print(repo_info)

    elif input_args.subcommand == "take_snapshot":
        (region, host) = parse_es_url(input_args.es_url)
        awsauth = get_awsauth(region)
        es = get_signed_es(host, awsauth)

        snapshot_body = get_snapshot_body(input_args.index_name)
        try:
            take_snapshot(
                es=es,
                repo_name=input_args.repo_name,
                index_name=input_args.index_name,
                snapshot_body=snapshot_body,
            )
        except Exception as err:
            import pdb

            pdb.set_trace()
            logger.debug(err)

    elif input_args.subcommand == "delete_snapshot":
        (region, host) = parse_es_url(input_args.es_url)
        awsauth = get_awsauth(region)
        es = get_signed_es(host, awsauth)

        delete_snapshot(
            es=es, repo_name=input_args.repo_name, index_name=input_args.index_name
        )

    elif input_args.subcommand == "snapshot_info":
        (region, host) = parse_es_url(input_args.es_url)
        awsauth = get_awsauth(region)
        es = get_signed_es(host, awsauth)
        is_snapshot_ok(es, input_args.repo_name, index_name=input_args.index_name)

    elif input_args.subcommand == "put_samples":
        (region, host) = parse_es_url(input_args.es_url)
        awsauth = get_awsauth(region)
        es = get_signed_es(host, awsauth)

        put_test_document(es, input_args.index_name)


def register_base_args(sub_parser):
    sub_parser.add_argument("es_url", type=str, help="ElasticSearch url")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tool that allow take ElasticSearch snapshots manually",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(help="Available commands")
    sub_commands = []

    #
    parser_register_new = subparsers.add_parser(
        "register-repository", help="Register new snapshot repository"
    )
    parser_register_new.add_argument(
        "-s3-bucket",
        nargs=2,
        type=str,
        metavar=("s3_bucket_name", "s3_bucket_region"),
        help="S3 bucket name and region",
    )
    parser_register_new.add_argument("-arn", type=str, help="AWS Role ARN")
    parser_register_new.add_argument("-repo-name", type=str, help="New repository name")
    parser_register_new.set_defaults(subcommand="register_new")
    sub_commands.append(parser_register_new)

    # -----------
    parser_repo_info = subparsers.add_parser(
        "repo-info", help="Get information about snapshot repository"
    )
    parser_repo_info.add_argument("-repo-name", type=str, help="Repository name")
    parser_repo_info.set_defaults(subcommand="repo_info")
    sub_commands.append(parser_repo_info)

    # -----------
    parser_take_snapshot = subparsers.add_parser(
        "take-snapshot", help="Initiate creation of new snapshot"
    )
    parser_take_snapshot.add_argument("-repo-name", type=str, help="Repository name")
    parser_take_snapshot.add_argument(
        "-index-name", type=str, help="ElasticSearch index name"
    )
    parser_take_snapshot.set_defaults(subcommand="take_snapshot")

    sub_commands.append(parser_take_snapshot)

    # -----------
    parser_delete_snapshot = subparsers.add_parser(
        "delete-snapshot", help="Delete snapshot"
    )
    parser_delete_snapshot.add_argument("-repo-name", type=str, help="Repository name")
    parser_delete_snapshot.add_argument(
        "-index-name", type=str, help="ElasticSearch index name"
    )
    parser_delete_snapshot.set_defaults(subcommand="delete_snapshot")

    sub_commands.append(parser_delete_snapshot)

    # -----------
    parser_snapshot_info = subparsers.add_parser(
        "snapshot-info", help="Get snapshot information"
    )
    parser_snapshot_info.add_argument("-repo-name", type=str, help="Repository name")
    parser_snapshot_info.add_argument(
        "-index-name", type=str, help="ElasticSearch index name"
    )
    parser_snapshot_info.set_defaults(subcommand="snapshot_info")
    sub_commands.append(parser_snapshot_info)

    # -----------
    parser_put_samples = subparsers.add_parser(
        "put-samples", help="Put sample documents"
    )
    parser_put_samples.add_argument(
        "-index-name", type=str, help="ElasticSearch index name"
    )
    parser_put_samples.set_defaults(subcommand="put_samples")
    sub_commands.append(parser_put_samples)

    list(map(register_base_args, sub_commands))

    input_args = parser.parse_args()

    if len(vars(input_args)) == 0:
        parser.print_help()
        sys.exit(1)

    cli_entrypoint(input_args)
