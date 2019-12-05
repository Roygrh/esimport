from datetime import datetime
from time import sleep

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import ConferencesSyncer


def test_conference_syncer():
    cs = ConferencesSyncer()
    cs.setup()

    # if tabele is already there it passes silently
    cs.aws.create_dynamodb_table(cs.config.dynamodb_table)
    # allow the table to be created
    sleep(2)
    cs.process_conferences_from_id(1, "2000-01-01")

    assert cs.sns_buffer._current_bytes_size == 4532
