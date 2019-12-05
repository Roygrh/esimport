from datetime import datetime
from time import sleep

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import PropertiesSyncer


def test_session_syncer():
    ps = PropertiesSyncer()
    ps.setup()

    # if tabele is already there it passes silently
    ps.aws.create_dynamodb_table(ps.config.dynamodb_table)
    # allow the table to be created
    sleep(2)
    ps.process_properties_from_id(1)

    assert ps.sns_buffer._current_bytes_size == 6222
