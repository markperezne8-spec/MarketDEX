import sqlite3
from pathlib import Path
from core.database_manager import DatabaseManager
from core.runtime_database_migration import migrate_legacy_database_if_needed
from services.inventory_app_service import InventoryAppService


def test_empty_runtime_recovers_legacy_inventory_once(tmp_path):
    legacy = tmp_path / 'data' / 'm51_m55_acceptance.sqlite3'
    runtime = tmp_path / 'runtime' / 'marketdex.sqlite3'
    service = InventoryAppService(legacy)
    service.add_asset(asset_id='asset-1', asset_name='Test ETB', asset_type='SEALED', quantity=1, total_cost_minor=10000, request_id='add-1')
    DatabaseManager(runtime).initialize()
    migrated = migrate_legacy_database_if_needed(runtime, tmp_path)
    assert migrated == legacy
    assert InventoryAppService(runtime).list_inventory()[0]['asset_name'] == 'Test ETB'


def test_nonempty_runtime_is_never_overwritten(tmp_path):
    legacy = tmp_path / 'data' / 'm51_m55_acceptance.sqlite3'
    runtime = tmp_path / 'runtime' / 'marketdex.sqlite3'
    legacy_service = InventoryAppService(legacy)
    legacy_service.add_asset(asset_id='legacy', asset_name='Legacy ETB', asset_type='SEALED', quantity=1, total_cost_minor=10000, request_id='legacy')
    runtime_service = InventoryAppService(runtime)
    runtime_service.add_asset(asset_id='runtime', asset_name='Runtime ETB', asset_type='SEALED', quantity=1, total_cost_minor=12000, request_id='runtime')
    assert migrate_legacy_database_if_needed(runtime, tmp_path) is None
    assert [row['asset_name'] for row in InventoryAppService(runtime).list_inventory()] == ['Runtime ETB']
