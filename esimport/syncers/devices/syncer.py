import os
import time
from datetime import datetime, timezone

from esimport.core import Record, SyncBase
from .ddb_syncer import DeviceDdbSyncer
from esimport.config import DYNAMODB_TABLE_NAME, AWS_REGION, DDB_QUERY_LIMIT


class DeviceSyncer(SyncBase):

    """
    Synchronize devices exclusively from DynamoDB,
    delegating data retrieval to DeviceDdbSyncer.
    """

    def __init__(self):
        super().__init__()
        # Dependency injection: pass params to helper
        self.ddb_helper = DeviceDdbSyncer(
            region=AWS_REGION,
            table_name=DYNAMODB_TABLE_NAME,
            query_limit=DDB_QUERY_LIMIT,
        )

    def sync(self, start_date: datetime):
        start_dt = start_date.astimezone(timezone.utc)
        end_dt = datetime.now(timezone.utc)

        for item in self.ddb_helper.fetch_from_ddb(start_dt, end_dt):
            record = Record(
                index=self.get_target_elasticsearch_index(item["DateUTC"]),
                id=None,
                body=item,
            )
            self.add_record(record)