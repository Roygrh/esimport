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

    def __init__(self):
        super().__init__()
        self.sqs = boto3.client(
            "sqs", endpoint_url=f"{self.config.aws_endpoint_url}:{self.config.sqs_port}"
        )

    def deserialize_message(self, message_body: str) -> list:
        return orjson.loads(orjson.loads(message_body)["Message"])

    def str_to_datetime(self, session: dict) -> dict:
        datetime_field = ["LoginTime", "LogoutTime"]
        for k, v in session.items():
            if k in datetime_field:
                session[k] = datetime.fromisoformat(v)
        return session

    def receive(self) -> str:
        response = self.sqs.receive_message(
            QueueUrl=self.config.sqs_queue_url,
            AttributeNames=["All"],
            VisibilityTimeout=15,
            WaitTimeSeconds=20,
            MaxNumberOfMessages=1,
        )
        if response.get("Messages"):
            messages = self.deserialize_message(response["Messages"][0]["Body"])
            for message in messages:
                service_area = message.get("ServiceArea")
                prop_by_service_area = self.get_and_cache_property_by_service_area_org_number(
                    service_area
                )
                if prop_by_service_area:
                    message = self.str_to_datetime(message)
                    record_date = message[self.record_date_fieldname]
                    session_record = Record(
                        _index=self.get_target_elasticsearch_index(record_date),
                        _type=self.record_type,
                        _source=message,
                        _date=record_date,
                    )

                    self.append_site_values(
                        session_record,
                        session_record.raw.get("ServiceArea"),
                        self.date_fields_to_localize,
                    )
                    print(f"SESSION RECORD: {session_record}")
                    self.add_record(session_record)
                    self.info(f"{session_record.raw['ID']}")
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
