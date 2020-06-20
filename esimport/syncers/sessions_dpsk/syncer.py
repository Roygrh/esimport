import boto3
import json
import orjson
from datetime import datetime
from dateutil import parser
from esimport.core import SyncBase, PropertiesMixin, Record

from ._schema import DPSKSessionSchema


class DPSKSessionSyncer(SyncBase, PropertiesMixin):
    target_elasticsearch_index_prefix: str = "sessions"
    uses_date_partitioned_index: bool = True

    incoming_data_schema = DPSKSessionSchema

    record_date_fieldname: str = "LogoutTime"

    record_type = "session"

    date_fields_to_localize = (
        ("LoginTime", "LoginTimeLocal"),
        ("LogoutTime", "LogoutTimeLocal"),
    )

    def deserialize_message(self, message_body: str) -> list:
        records = orjson.loads(message_body)
        return [records] if isinstance(records, dict) else records

    def str_to_datetime(self, session: dict) -> dict:
        datetime_field = ["LoginTime", "LogoutTime"]
        for k, v in session.items():
            if k in datetime_field:
                try:
                    session[k] = parser.isoparse(v)
                except TypeError:
                    # TODO: probably we need an alert here
                    session[k] = ""
        return session

    def receive(self) -> str:
        self.info("Checking for new ppk messages..")
        response = self.aws.sqs_receive_messages(
            sqs_queue_url=self.config.ppk_sqs_queue_url
        )
        messages = response.get("Messages")
        if messages:
            self.debug(f"Got this message from SQS: {messages}")

            records_str = response["Messages"][0]["Body"]
            receipt_handle = response["Messages"][0]["ReceiptHandle"]

            try:
                records = self.deserialize_message(records_str)
            except json.decoder.JSONDecodeError:
                # Malformed message, move to DLQ
                records = []
                self.aws.sqs_send_mesage(
                    queue_url=self.config.ppk_dlq_queue_url, message_body=records_str
                )

            for record in records:
                resident_id = record.get("ResidentID")
                if not resident_id:
                    resident_id = record.get("ResidentId")

                service_area = record.get("ServiceArea")
                session_id = record.get("SessionID")
                unique_id = f"{service_area}:{session_id}"

                ppk_type = record.get("PpkType")

                record = self.str_to_datetime(record)
                record.update({"is_ppk": True})
                record.update({"RECORD_ID": unique_id})
                record.update({"Name": resident_id})
                record.update({"PpkType": ppk_type})

                record_date = record[self.record_date_fieldname]
                session_record = Record(
                    _index=self.get_target_elasticsearch_index(record_date),
                    _type=self.record_type,
                    _source=record,
                    _date=record_date,
                )

                self.append_site_values(
                    session_record, service_area, self.date_fields_to_localize,
                )

                self.add_record(session_record, flush=True, update_cursor=False)

            self.aws.sqs_delete_message(
                sqs_queue_url=self.config.ppk_sqs_queue_url,
                receipt_handle=receipt_handle,
            )
            return response["Messages"][0]["MessageId"]

        return ""

    def sync(self, start_date: datetime = None):
        while True:
            message_id = self.receive()
            if not message_id:
                self.info(
                    f"[Delay] Waiting {self.config.sns_calls_wait_in_seconds} seconds"
                )
                self.sleep(self.config.sns_calls_wait_in_seconds)
