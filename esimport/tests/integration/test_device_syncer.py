from datetime import datetime
from time import sleep

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import DeviceSyncer


def test_device_syncer():
    ds = DeviceSyncer()
    ds.setup()

    # if tabele is already there it passes silently
    ds.aws.create_dynamodb_table(ds.config.dynamodb_table)
    # allow the table to be created
    sleep(2)
    ds.process_devices_from_id(1, "2000-01-01")

    assert ds.sns_buffer._current_bytes_size == 472

