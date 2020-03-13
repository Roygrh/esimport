import time
from datetime import datetime, timezone
from typing import Generator

from esimport.core import PropertiesMixin, Record, SyncBase

from ._queries import GET_DEVICES_ANCESTOR_ORG_NUMBER_TREE_QUERY, GET_DEVICES_QUERY
from ._schema import DeviceSchema


class DeviceSyncer(SyncBase, PropertiesMixin):

    target_elasticsearch_index_prefix: str = "devices"
    uses_date_partitioned_index: bool = True

    # How the data going to look like?
    # Just take a look at `_schema.py` file
    incoming_data_schema = DeviceSchema

    default_query_limit: int = 500

    # the field to consider its value as the record _date (and even a version)
    # it has to be a field holding a datetime object
    record_date_fieldname: str = "DateUTC"

    # the type of the record for Elasticsearch
    record_type = "device"

    # These dates are in 'America/Los_Angeles' format
    dates_from_pacific = {"Date": "DateUTC"}

    dates_to_localize = (("DateUTC", "DateLocal"),)

    def process_devices_from_id(self, next_id: int, start_date: datetime) -> (int, int):
        count = 0
        up_to = next_id + self.default_query_limit

        self.debug(f"Get Devices from {next_id} to {up_to} since {start_date}")

        for device in self.get_devices(next_id, self.default_query_limit, start_date):
            count += 1
            self.debug(f"Record found: {device.id}")
            service_area = device.raw.get("ServiceArea")
            self.append_site_values(device, service_area, self.dates_to_localize)

            self.add_record(device)
            next_id = device.id + 1

        return count, next_id

    def sync(self, start_date: datetime):
        """
        Loop to continuously find new Devices and push them to AWS SQS
        """
        next_id_to_process = self.max_id() + 1
        timer_start = time.time()
        while True:
            count, next_id_to_process = self.process_devices_from_id(
                next_id_to_process, start_date
            )

            elapsed_time = int(time.time() - timer_start)

            # habitually reset mssql connection.
            if count == 0 or elapsed_time >= self.database_connection_reset_limit:
                self.info(
                    f"[Delay] Reset SQL connection and waiting {self.db_wait} seconds"
                )
                self.mssql.reset()
                time.sleep(self.db_wait)
                timer_start = time.time()  # reset timer

    def get_devices(self, start, limit, start_date="1900-01-01"):

        for device in self.fetch_rows_as_dict(
            GET_DEVICES_QUERY, limit, start, start_date
        ):
            for key in list(device.keys()):
                if isinstance(device[key], datetime):
                    if key in self.dates_from_pacific:
                        device[
                            self.dates_from_pacific[key]
                        ] = self.convert_pacific_to_utc(
                            self.set_pacific_timezone(device[key])
                        )
                        # As there's no `Date` field in ElevenAPI's Device model
                        del device[key]
                    else:
                        device[key] = self.set_utc_timezone(device[key])

            org_number_tree = []

            # FIXME: this is very slow, causing the devices records to stay way behind on PROD
            # find a better way to attach the org_number tree for devices. this must NOT be done for EACH device!
            # org_number_tree_query = self.query_get_org_number_tree()
            # for org in list(self.fetch(org_number_tree_query, row['ID'])):
            #     org_number_tree.append(org[0])
            device["AncestorOrgNumberTree"] = org_number_tree

            record_date = device[self.record_date_fieldname]
            yield Record(
                _index=self.get_target_elasticsearch_index(record_date),
                _type=self.record_type,
                _source=device,
                _date=record_date,
            )
