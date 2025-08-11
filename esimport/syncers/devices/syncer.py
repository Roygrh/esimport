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

        # Dependency injection: pass params to helper
        self.ddb_helper = DeviceDdbSyncer(
            region=AWS_REGION,
            table_name=DYNAMODB_TABLE_NAME,
            query_limit=query_limit,
        )

    def sync(self, start_date: datetime):
        """
        Query DynamoDB for items between start_date and now,
        convert each item to a Record, and add it to the buffer.
        """
        # Define UTC time window
        start_dt = start_date.astimezone(timezone.utc)
        end_dt = datetime.now(timezone.utc)

        # Fetch items from DynamoDB via helper
        for item in self.ddb_helper.fetch_from_ddb(start_dt, end_dt):
            # Map full item into document body
            body = { key: item.get(key) for key in item }
            # Create Record without id so ES generates its own
            record = Record(
                index=self.get_target_elasticsearch_index(body['DateUTC']),
                id=None,
                body=body
            )
            self.add_record(record)