from datetime import datetime
from time import sleep

from esimport.core import SyncBase, PropertiesMixin
from esimport.syncers import AccountsSyncer


def test_account_syncer():
    ac = AccountsSyncer()
    ac.setup()

    # if tabele is already there it passes silently
    ac.aws.create_dynamodb_table(ac.config.dynamodb_table)
    # allow the table to be created
    sleep(2)
    ac.put_item_in_dynamodb_table("account", 0, datetime(2019, 1, 1))
    ac.update(datetime(2019, 1, 1))
    ac.process_accounts_from_id(2, "2000-01-01")

    assert ac.sns_buffer._current_bytes_size == 22446
