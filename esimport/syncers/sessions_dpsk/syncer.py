import boto3
import json
import orjson
from datetime import datetime
from datetime import timedelta
from dateutil import parser
from esimport.core import SyncBase, PropertiesMixin, Record

from ._schema import DPSKSessionSchema
import traceback

# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER
MAX_SAFE_JSON_INT = 9007199254740992

SEVEN_DAYS = 604800 # 7 * 60 * 60 * 24

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

    def adjust_to_safe_json_int(self, record: dict) -> None:
        record["SessionLength"] = SEVEN_DAYS
        record["LogoutTime"] = record["LoginTime"] + timedelta(days=7)



    def receive(self) -> str:
        try:
            self.info("Checking for new ppk messages..")
            response = self.aws.sqs_receive_messages(
                sqs_queue_url=self.config.ppk_sqs_queue_url
            )
            messages = response.get("Messages",[])
            self.debug(f"Got this message from SQS: {messages}")
            messages_delete_buffer = []
        except Exception as err:
            self.warning(f"err: {err}")
            traceback.print_exc()
        for message in messages:
            records_str = message["Body"]
            try:
                records = self.deserialize_message(records_str)
            except json.decoder.JSONDecodeError as e:
                self.warning(f"deserialize_message failed -> {e.msg}\n{records_str}")
                # Malformed message, move to DLQ
                records = []
                self.aws.sqs_send_mesage(
                    queue_url=self.config.ppk_dlq_queue_url, message_body=records_str
                )
            try:
                for record in records:
                    resident_id = record.get("ResidentID")
                    if not resident_id:
                        resident_id = record.get("ResidentId")

                    service_area = record.get("ServiceArea")
                    session_id = record.get("SessionID")
                    unique_id = f"{service_area}:{session_id}"

                    ppk_type = record.get("PpkType")

                    record = self.str_to_datetime(record)

                    # JSON only support 2^53 - 1 int numbers
                    # somehow incoming data in SessionsLength can be bigger that that
                    # handling this case
                    if record['SessionLength'] > MAX_SAFE_JSON_INT:
                        self.adjust_to_safe_json_int(record)


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
                    self.report_old_record(session_record)

                    self.append_site_values(
                        session_record, service_area, self.date_fields_to_localize,
                    )


                    self.add_record(session_record, update_cursor=False)

                # Delete message from SQS in batch
                messages_delete_buffer.append({"Id": message["MessageId"],"ReceiptHandle": message["ReceiptHandle"]})

            except Exception as err:
                self.log(f"err: {err}")
                traceback.print_exc()
        if messages_delete_buffer:
            self.aws.sqs_delete_messages(self.config.ppk_sqs_queue_url,messages_delete_buffer)
        return ""

    def sync(self, start_date: datetime = None):
        while True:
            message_id = self.receive()
            if not message_id:
                self.update_current_date()
                self.info(
                    f"[Delay] Waiting {self.config.sns_calls_wait_in_seconds} seconds"
                )
                self.sleep(self.config.sns_calls_wait_in_seconds)
