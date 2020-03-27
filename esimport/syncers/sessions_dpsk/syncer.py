import boto3
import orjson
from datetime import datetime

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
        records = orjson.loads(orjson.loads(message_body))
        return [records] if isinstance(records, dict) else records

    def str_to_datetime(self, session: dict) -> dict:
        datetime_field = ["LoginTime", "LogoutTime"]
        for k, v in session.items():
            if k in datetime_field:
                session[k] = datetime.fromisoformat(v)
        return session

    def receive(self) -> str:
        self.info("Checking for new ppk messages..")
        response = self.aws.ppk_sqs_queue_client.receive_message(
            QueueUrl=self.config.dpsk_sqs_queue_url,
            AttributeNames=["All"],
            VisibilityTimeout=15,
            WaitTimeSeconds=20,
            MaxNumberOfMessages=1,
        )
        messages = response.get("Messages")
        if messages:
            self.debug(f"Got this message from SQS: {messages}")
            records = self.deserialize_message(response["Messages"][0]["Body"])
            receipt_handle = response["Messages"][0]["ReceiptHandle"]
            for record in records:
                service_area = record.get("ServiceArea")
                prop_by_service_area = self.get_and_cache_property_by_service_area_org_number(
                    service_area
                )
                if prop_by_service_area:
                    record = self.str_to_datetime(record)
                    record.update({"is_ppk": True})
                    record_date = record[self.record_date_fieldname]
                    session_record = Record(
                        _index=self.get_target_elasticsearch_index(record_date),
                        _type=self.record_type,
                        _source=record,
                        _date=record_date,
                    )

                    self.append_site_values(
                        session_record,
                        session_record.raw.get("ServiceArea"),
                        self.date_fields_to_localize,
                    )

                    self.add_record(session_record, flush=True, update_cursor=False)

            self.aws.ppk_sqs_queue_client.delete_message(
                QueueUrl=self.config.dpsk_sqs_queue_url, ReceiptHandle=receipt_handle
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
