import logging
from dataclasses import dataclass
from typing import Any, List, Union

import boto3
import orjson

from .record import Record


@dataclass
class SNSBuffer:
    sns_client: Any
    dunamodb_table_client: Any
    topic_arn: str
    max_sns_bulk_send_size_in_bytes: int
    logging: logging.Logger

    _records_list: List[dict] = []
    _last_added_record: Union[Union, None] = None
    _current_bytes_size: int = 0

    def add_record(self, record: Record):
        """
        This adds a record to an internal records list and auto decides whether it's time 
        to send to SNS or not. Depending if the records list's size in bytes reached the SNS
        max message size threshold or not.
        Once some records are sent to SNS, it resets the list and starts over.
        """
        record_size = self._get_record_size(record)

        if self._should_flush(record):
            self._flush()
            self._update_cursor_state()

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

    def _flush(self):
        self._send_to_sns()
        self._records_list = []
        self._current_bytes_size = 0

    def _update_cursor_state(self):
        response = self.dynamodb_table_client.put_item(
            Item={
                "doctype": self._last_added_record._type,
                "latest_id": self._last_added_record._id,
                "latest_date": self._last_added_record._date,
            }
        )

    def _send_to_sns(self):
        message = orjson.dumps(self._records_list).decode("utf-8")
        response = self.sns_client.publish(TopicArn=self.topic_arn, Message=message)
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception  # TODO: raise a proper exception

    def _get_record_size(self, record: Record) -> int:
        record_as_bytes = orjson.dumps(record.as_dict())
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
