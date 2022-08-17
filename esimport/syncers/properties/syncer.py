import time
from datetime import datetime, timezone
from typing import Generator

from esimport.core import PropertiesMixin, Record, SyncBase

from ._queries import GET_PROPERTIES_QUERY
from ._schema import Property


class PropertiesSyncer(SyncBase, PropertiesMixin):

    target_elasticsearch_index_prefix: str = "properties"
    uses_date_partitioned_index: bool = False

    # How the data going to look like?
    # Just take a look at `_schema.py` file
    incoming_data_schema = Property

    default_query_limit: int = 50

    # the field to consider its value as the record _date (and even a version)
    # it has to be a field holding a datetime object
    record_date_fieldname: str = "UpdateTime"

    # the type of the record for Elasticsearch
    record_type = "property"

    def process_properties_from_id(self, next_id_to_process: int) -> (int, int):
        count = 0
        for record in self.get_properties(next_id_to_process, self.default_query_limit):
            count += 1
            self.debug(f"Record found: {record.id}")
            org_num = record.raw.get("Number")
            org_num_key = self._cache_key_for_org_number(org_num)

            # Add both Property/Organization Number and Service Areas to the cache
            self.cache_client.set(org_num_key, record.raw)

            for service_area_obj in record.raw.get("ServiceAreaObjects"):
                self.cache_client.set(service_area_obj["Number"], org_num_key)

            self.add_record(record)
            next_id_to_process = record.id

        return count, next_id_to_process

    def sync(self, start_date: datetime = None):
        """
        Continuously update ElasticSearch to have the latest Property data
        """
        next_id_to_process = 0
        timer_start = time.time()
        while True:
            count, next_id_to_process = self.process_properties_from_id(
                next_id_to_process
            )
            elapsed_time = int(time.time() - timer_start)

            # habitually reset mssql connection.
            if count == 0 or elapsed_time >= self.database_connection_reset_limit:
                wait = self.db_wait * 2
                self.info(f"[Delay] Reset SQL connection and waiting {wait} seconds")
                self.mssql.reset()
                time.sleep(wait)
                timer_start = time.time()  # reset timer
                # start over again when all records have been processed
                if count == 0:
                    next_id_to_process = 0

    def get_properties(self, start, limit):
        self.debug(
            f"Fetching properties from Organization.ID >= {start} (limit: {limit})"
        )

        for row in list(self.fetch_rows_as_dict(GET_PROPERTIES_QUERY, limit, start)):
            self._set_additonal_property_info(row)
            self.info(f"debug row {row}")
            record_date = row[self.record_date_fieldname]
            yield Record(
                _index=self.get_target_elasticsearch_index(record_date),
                _type=self.record_type,
                _source=row,
                _date=record_date,
            )
