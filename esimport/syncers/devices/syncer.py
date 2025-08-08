import os
import time
from datetime import datetime, timezone

from esimport.core import Record, SyncBase
from .ddb_syncer import DeviceDdbSyncer


class DeviceSyncer(SyncBase):

    """
    Synchronize devices exclusively from DynamoDB,
    delegating data retrieval to DeviceDdbSyncer.
    """
    # Instantiate helper using values from Config
    ddb_helper = DeviceDdbSyncer()

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