import os
import abc
import logging
import time
from datetime import datetime, timezone
from typing import List

from dateutil import tz, parser
from esimport.infra import AmazonWebServices, CacheClient, MsSQLHandler

from .base_schema import BaseSchema
from .config import Config
from .exceptions import ESImportImproperlyConfigured
from .record import Record
from .sns_buffer import SNSBuffer
import sentry_sdk
from dotenv import load_dotenv
import datadog


here_path = os.path.dirname(__file__)
parent_path = os.path.dirname(here_path)
root_path = os.path.dirname(parent_path)
dotenv_path = os.path.join(root_path, ".env")

load_dotenv(dotenv_path, override=True)


class SyncBase(abc.ABC):
    target_elasticsearch_index_prefix: str
    uses_date_partitioned_index: bool
    incoming_data_schema: BaseSchema

    current_date: str = datetime.utcnow().strftime("%Y-%m")
    current_date_month_fixed: bool = False
    target_index_date: str

    default_query_limit: int

    # the field to consider its value as the record version
    version_fieldname: str

    record_type: str = None

    count_to_be_imported_from_sql: int

    def __init__(self):
        self.config = self.get_config()
        self.logger = self.setup_logger(self.config.log_level)

    def get_config(self):
        try:
            return Config()
        except ValueError as e:
            raise ESImportImproperlyConfigured(str(e))

    def setup_logger(self, level: str):
        logging.basicConfig()
        logger = logging.getLogger(f"esimport - {self.record_type} syncer")
        logger.setLevel(level.upper())
        return logger

    def setup(self):
        # Setup MSSQL
        self.mssql = MsSQLHandler(
            dsn=self.config.mssql_dsn,
            database_info=self.config.database_info,
            database_query_timeout=self.config.database_query_timeout,
            database_connection_timeout=self.config.database_connection_timeout,
            logger=self.logger,
        )

        # Setup AWS
        ports_mappings = {
            "s3": self.config.s3_port,
            "sns": self.config.sns_port,
            "dynamodb": self.config.dynamodb_port,
            "sqs": self.config.sqs_port,
        }
        self.aws = AmazonWebServices(
            endpoint_url=self.config.aws_endpoint_url,
            aws_access_key_id=self.config.aws_access_key_id,
            aws_secret_access_key=self.config.aws_secret_access_key,
            region_name=self.config.aws_default_region,
            ports_mappings=ports_mappings,
            logger=self.logger,
        )

        # Setup Redis Cache
        self.cache_client = CacheClient(
            redis_host=self.config.redis_host,
            redis_port=self.config.redis_port,
            logger=self.logger,
        )

        # Setup the SNS buffer that's going to be responsibe of sending messages
        # to SNS
        self.sns_buffer = SNSBuffer(
            sns_client=self.aws.sns_resource.meta.client,
            dynamodb_table_client=self.dynamodb_table,
            topic_arn=self.config.sns_topic_arn,
            max_sns_bulk_send_size_in_bytes=self.config.max_sns_bulk_send_size_in_bytes,
            logger=self.logger,
        )

        self.sns_buffer.on_flushed = self.flushed

        datadog.initialize(
            api_key=self.config.datadog_api_key, host_name=self.config.datadog_env
        )

    def flushed(self, no_of_records):
        # send to datadog
        datadog.api.Metric.send(
            metric=self.record_type + "CountToBeImportedFromSql",
            points=no_of_records,
        )

    @abc.abstractmethod
    def sync(self, star_date: datetime = None):
        raise NotImplementedError

    def add_record(
        self, record: Record, flush=False, update_cursor=True, cursor_name=None
    ):
        self.sns_buffer.add_record(
            record, flush=flush, update_cursor=update_cursor, cursor_name=cursor_name
        )

    def fetch_rows_as_dict(self, query, *args) -> List[dict]:
        return self.mssql.fetch_rows_as_dict(query, *args)

    def execute_query(self, query, *args):
        return self.mssql.execute(query, *args)

    def fetch_rows(self, query, *args, column_names=None):
        return self.mssql.fetch_rows(query, *args, column_names=column_names)

    def get_target_elasticsearch_index(self, rec_date: datetime = None) -> str:
        # Target index name for this record in Elasticsearch
        if self.uses_date_partitioned_index:
            if rec_date:
                target_index_date = rec_date.strftime("%Y-%m")
                self.target_index_date = target_index_date
                return f"{self.target_elasticsearch_index_prefix}-{target_index_date}"

            raise ESImportImproperlyConfigured

        return self.target_elasticsearch_index_prefix

    def put_item_in_dynamodb_table(
        self, doctype: str, latest_id: int, latest_date: datetime
    ):
        response = self.dynamodb_table.put_item(
            Item={
                "doctype": doctype,
                "latest_id": latest_id,
                "latest_date": latest_date.isoformat(),
            }
        )
        self.log(str(response), logging.DEBUG)
        return response

    @property
    def dynamodb_table(self):
        return self.aws.dynamodb_resource.Table(self.config.dynamodb_table)

    @property
    def last_inserted_cursor_state(self):
        return self.dynamodb_table.get_item(
            Key={"doctype": self.record_type}, ConsistentRead=True
        )

    def max_id(self):
        return self.last_inserted_cursor_state["Item"].get("latest_id", 0)

    def latest_date(self) -> datetime:
        dt_str = self.last_inserted_cursor_state["Item"].get(
            "latest_date", "1900-01-01"
        )
        return parser.parse(dt_str).replace(tzinfo=timezone.utc)

    @staticmethod
    def set_utc_timezone(datetime_object: datetime) -> datetime:
        if not datetime_object:
            return None

        assert isinstance(datetime_object, datetime), "Object is not a datetime object."
        return datetime_object.replace(tzinfo=timezone.utc)

    @staticmethod
    def convert_utc_to_local_time(datetime_object: datetime, tzone):
        if not datetime_object:
            return None

        if datetime_object.tzinfo != timezone.utc:
            datetime_object = datetime_object.replace(tzinfo=timezone.utc)

        local_datetime = datetime_object.astimezone(tz.gettz(tzone))
        return local_datetime.replace(tzinfo=tz.gettz(tzone))

    @staticmethod
    def convert_pacific_to_utc(datetime_object: datetime):
        if not datetime_object:
            return None

        assert isinstance(
            datetime_object, datetime
        ) and datetime_object.tzinfo == tz.gettz(
            "America/Los_Angeles"
        ), "Time zone is not set to America/Los_Angeles."
        utc_datetime = datetime_object.astimezone(tz.gettz("UTC"))
        return utc_datetime.replace(tzinfo=tz.gettz("UTC"))

    @staticmethod
    def set_pacific_timezone(datetime_object: datetime):
        if not datetime_object:
            return None

        assert isinstance(datetime_object, datetime), "Object is not a datetime object."
        return datetime_object.replace(tzinfo=tz.gettz("America/Los_Angeles"))

    @staticmethod
    def sleep(seconds: float):
        time.sleep(seconds)

    def log(self, message: str, level: int = logging.INFO):
        self.logger.log(level, message)

    def debug(self, message: str):
        self.log(message, level=logging.DEBUG)

    def info(self, message: str):
        self.log(message, level=logging.INFO)

    def warning(self, message: str):
        self.log(message, level=logging.WARNING)

    @property
    def db_wait(self):
        return self.config.database_calls_wait_in_seconds

    @property
    def database_connection_reset_limit(self):
        return self.config.database_connection_reset_limit

    @property
    def db_sessions_gap_in_seconds(self):
        return self.config.db_sessions_gap_in_seconds

    def report_old_record(self, record: Record):
        """
        function to check if the es record being placed is of
        the current month's index or not.
        if it is not of the current month, report it via sentry

        Returns 'True' if it is reported
        """

        # check if current date and record's date are different
        if self.current_date != self.target_index_date:
            tags = {
                "current_date": self.current_date,
                "record_date": self.target_index_date,
                "index": record._index,
                "record_id": record.id,
            }
            # check if record's date is first day of the month
            # if it is, update current date and check again for
            # out of date record
            if record._date.day == 1:
                # the 'current_date_month_fixed' bool flag optimizes so
                # that we have to update date here only once
                if not self.current_date_month_fixed:
                    self.update_current_date()
                    self.current_date_month_fixed = True
                if self.current_date != self.target_index_date:
                    sentry_sdk.capture_message(
                        f"Out of date record being put detected",
                        level="info",
                        tags=tags,
                    )
                    return True
            else:
                self.current_date_month_fixed = False
                sentry_sdk.capture_message(
                    f"Out of date record being put detected", level="info", tags=tags
                )
                return True

    def update_current_date(self):
        """
        updates the current date stored
        is normally called when the sql connection is reset
        """
        self.current_date = datetime.utcnow().strftime("%Y-%m")
