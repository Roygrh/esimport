import os
import importlib
import pytest

from esimport.syncers.devices.syncer import run_device_sync

class DummySyncer:
    def fetch(self, *args, **kwargs):
        yield from []

@pytest.fixture(autouse=True)
def patch_sql_and_ddb(monkeypatch):
    # Placeholder syncers to detect which one is invoked
    monkeypatch.setenv("USE_DDB_DEVICES", "false")
    import esimport.syncers.devices.syncer as mod
    monkeypatch.setattr(mod, "DeviceSqlSyncer", lambda: DummySyncer())
    monkeypatch.setattr(mod, "DeviceDdbSyncer", lambda: (_ for _ in ()) )
    return mod

def test_sql_path(monkeypatch, capsys):
    # Flag to false → must use SQL
    monkeypatch.setenv("USE_DDB_DEVICES", "false")
    run_device_sync("a","b",limit=1)
    # No exceptions: go through SQL syncer

def test_ddb_path(monkeypatch):
    # Flag to true → must use DDB
    monkeypatch.setenv("USE_DDB_DEVICES", "true")
    import importlib
    import esimport.syncers.devices.syncer as mod
    importlib.reload(mod)
    # Replace DdbSyncer with DummySyncer
    mod.DeviceDdbSyncer = lambda: DummySyncer()
    run_device_sync("a","b",limit=1)
    # No exceptions: go through DDB syncer
