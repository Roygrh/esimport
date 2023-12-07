import logging
from dataclasses import dataclass, field
from bz2 import compress
from base64 import b64encode
from decimal import Decimal
from typing import Any, List, Union
from datetime import datetime
import boto3
import orjson
import time

from .record import Record
from .event import Event


@dataclass
class SNSBuffer:
    sns_client: Any
    dynamodb_table_client: Any
    topic_arn: str
    max_sns_bulk_send_size_in_bytes: int
    logger: logging.Logger

    _records_list: List[dict] = field(default_factory=lambda: [])
    _last_added_record: Union[Record, None] = None
    _current_bytes_size: int = 0
    last_flush_time: Union[datetime, None] = None
    _flushed = Event()

    def add_record(
        self, record: Record, flush=False, update_cursor=True, cursor_name=None
    ):
        """
        This adds a record to an internal records list and auto decides whether it's time
        to send to SNS or not. Depending if the records list's size in bytes reached the SNS
        max message size threshold or not.
        Once some records are sent to SNS, it resets the list and starts over.
        """
        record_size = self._get_record_size(record)
        if flush or self._should_flush(record_size):
            self._flush()

            if update_cursor:
                self._update_cursor_state(cursor_name)

        self._records_list.append(record.as_dict())
        self._current_bytes_size += record_size
        self._last_added_record = record

    def _should_flush(self, new_record_size: int = 0) -> bool:
        """
        Did we reachthe threshold of max allowed SNS message size ?
        As of writing this, it's 256 KB.
        Which should be the same value of `self.max_sns_bulk_send_size_in_bytes` but in bytes.
        For more info, have a look at:
            https://aws.amazon.com/about-aws/whats-new/2013/06/18/amazon-sqs-announces-256KB-large-payloads/
        """

        return (
            self._current_bytes_size
            + new_record_size
            + self.list_json_encoding_size_overhead  # see why we need this below
            >= self.max_sns_bulk_send_size_in_bytes
        )

    @property
    def no_new_records_for_a_while(self):
        if not self.last_flush_time:
            # for the first time, `last_flush_time` will be None
            # let's init it with current time
            self.last_flush_time = datetime.utcnow()
            return False

        now = datetime.utcnow()
        seconds_passed = (now - self.last_flush_time).total_seconds()
        return seconds_passed >= 60

    def _flush(self):
        self._send_to_sns()
        list_length = len(self._records_list)
        self._flushed(list_length)
        self._records_list = []
        self._current_bytes_size = 0

    def _update_cursor_state(self, cursor_name=None):
        cn = cursor_name or self._last_added_record._type
        response = self.dynamodb_table_client.put_item(
            Item={
                "doctype": cn,
                "latest_id": self._last_added_record.id,
                "latest_date": self._last_added_record._date.isoformat(),
            }
        )
        self.log(str(response), logging.DEBUG)

    def _send_to_sns(self):
        message = self.orjson_dumps(self._records_list).decode("utf-8")
        message_length = len(message)
        list_length = len(self._records_list)
        self.log(
            f"About to send {list_length} records. Size: {message_length} bytes. Max is: {self.max_sns_bulk_send_size_in_bytes}",
            logging.DEBUG,
        )
        if message_length > self.max_sns_bulk_send_size_in_bytes:
            self.log(
                f"The sum of the following records ({message_length} bytes) exceed the SNS limits"
                f" {self.max_sns_bulk_send_size_in_bytes} bytes, compressing:",
                logging.DEBUG,
            )
            for _rec in self._records_list:
                self.log(f"Record ID: {_rec.get('_id')}")

            message = self._compress_large_message(message)
            message_length = len(message)
            self.log(
                f"New SNS message size after compression is: {message_length} bytes",
                logging.DEBUG,
            )

        response = self.sns_client.publish(TopicArn=self.topic_arn, Message=message)
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception  # TODO: raise a proper exception

    def _get_record_size(self, record: Record) -> int:
        record_as_bytes = self.orjson_dumps(record.as_dict())
        return len(record_as_bytes)

    @property
    def list_json_encoding_size_overhead(self):
        """
        Account for the extra brackets `[`, `]` and extra commas `,`  when serializing a list
        of dict to json, these shouldn't make the size of the mssage being sent to the SNS topic
        greater than `self.max_sns_bulk_send_size_in_bytes`.
        """
        initial_overhead = 2  # for '[' and ']'
        # then for the commas, for each record we're going to have a comma append to it
        # except the last one, so:
        return initial_overhead + len(self._records_list) - 1

    def log(self, message: str, level: int = logging.INFO):
        self.logger.log(level, message)

    # We are going to use orjson (see below), this function is a small wrapper
    # to match the standard json.dumps behavior.
    def orjson_dumps(self, v):
        def default(obj):
            if isinstance(obj, Decimal):
                return str(obj)

        # orjson.dumps returns bytes, to match standard json.dumps we need to call `.decode()`
        return orjson.dumps(v, default=default)  # .decode()

    def on_flushed(self, callback):
        self._flushed += callback

    def _compress_large_message(self, message):
        compressed_message = compress(message.encode("utf-8"))
        return b64encode(compressed_message).decode("utf-8")
