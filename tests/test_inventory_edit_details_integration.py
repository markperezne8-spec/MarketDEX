import pytest
from services.inventory_app_service import InventoryAppService
from services.inventory_edit_details_service import edit_inventory_details


def _service(tmp_path):
    service = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1', asset_name='Mistake ETB', asset_type='SINGLE', quantity=4, total_cost_minor=5000, request_id='seed-1')
    return service


def test_edit_details_corrects_name_and_type_without_mutating_inventory_authority(tmp_path):
    service = _service(tmp_path)
    with service.database.read_connection() as connection:
        before = dict(connection.execute("SELECT * FROM inventory_authority WHERE asset_id='asset-1'").fetchone())
        history = connection.execute("SELECT COUNT(*) n FROM inventory_history").fetchone()['n']
        movements = connection.execute("SELECT COUNT(*) n FROM inventory_movements").fetchone()['n']
    result = edit_inventory_details(service, asset_id='asset-1', asset_name='Correct ETB', asset_type='SEALED', request_id='edit-1')
    assert result['asset_name'] == 'Correct ETB'
    assert result['asset_type'] == 'SEALED'
    with service.database.read_connection() as connection:
        after = dict(connection.execute("SELECT * FROM inventory_authority WHERE asset_id='asset-1'").fetchone())
        assert after == before
        assert connection.execute("SELECT COUNT(*) n FROM inventory_history").fetchone()['n'] == history
        assert connection.execute("SELECT COUNT(*) n FROM inventory_movements").fetchone()['n'] == movements
        assert connection.execute("SELECT COUNT(*) n FROM event_identity WHERE event_type='INVENTORY_ASSET_DETAILS_EDITED'").fetchone()['n'] == 1
        assert connection.execute("SELECT COUNT(*) n FROM audit_events WHERE authority_type='INVENTORY_DETAILS_EDIT' AND verification_result='VERIFIED'").fetchone()['n'] == 1


def test_edit_details_rejects_archived_asset(tmp_path):
    service = _service(tmp_path)
    service.archive_asset(asset_id='asset-1', request_id='archive-1')
    with pytest.raises(ValueError, match='Archived inventory details cannot be edited'):
        edit_inventory_details(service, asset_id='asset-1', asset_name='Correct ETB', asset_type='SEALED', request_id='edit-1')


def test_edit_details_rejects_noop_and_invalid_type(tmp_path):
    service = _service(tmp_path)
    with pytest.raises(ValueError, match='Change the asset name or type'):
        edit_inventory_details(service, asset_id='asset-1', asset_name='Mistake ETB', asset_type='SINGLE', request_id='edit-noop')
    with pytest.raises(ValueError, match='Unsupported asset type'):
        edit_inventory_details(service, asset_id='asset-1', asset_name='Mistake ETB', asset_type='INVALID', request_id='edit-invalid')
