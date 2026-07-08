import pytest
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService


def _service(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1',asset_name='Mistake ETB',asset_type='SINGLE',quantity=4,total_cost_minor=5000,request_id='seed-1')
    service.add_asset(asset_id='asset-2',asset_name='Charizard ex',asset_type='SINGLE',quantity=3,total_cost_minor=1000,request_id='seed-2')
    return service


def test_archive_removes_asset_from_active_inventory_without_deleting_evidence(tmp_path):
    service=_service(tmp_path)
    with service.database.read_connection() as connection:
        before_history=connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n']
        before_movements=connection.execute('SELECT COUNT(*) n FROM inventory_movements').fetchone()['n']
    archived=service.archive_asset(asset_id='asset-1',request_id='archive-1')
    assert archived['state']=='CANCELLED'
    assert [row['asset_id'] for row in service.list_inventory()]==['asset-2']
    with service.database.read_connection() as connection:
        assert connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n']==before_history
        assert connection.execute('SELECT COUNT(*) n FROM inventory_movements').fetchone()['n']==before_movements
        assert connection.execute("SELECT COUNT(*) n FROM event_identity WHERE event_type='INVENTORY_ASSET_ARCHIVED'").fetchone()['n']==1
        assert connection.execute("SELECT COUNT(*) n FROM audit_events WHERE authority_type='INVENTORY_ARCHIVE' AND verification_result='VERIFIED'").fetchone()['n']==1
        assert connection.execute("SELECT COUNT(*) n FROM assets WHERE asset_id='asset-1'").fetchone()['n']==1
        assert connection.execute("SELECT COUNT(*) n FROM inventory_authority WHERE asset_id='asset-1'").fetchone()['n']==1


def test_archive_updates_active_mission_control_projection(tmp_path):
    service=_service(tmp_path); mission=MissionControlService(tmp_path/'marketdex.sqlite3')
    service.archive_asset(asset_id='asset-1',request_id='archive-1')
    snapshot=mission.snapshot()
    assert snapshot['inventory_asset_count']==1
    assert snapshot['inventory_units']==3
    assert snapshot['inventory_cost_minor']==1000


def test_archive_is_exactly_once_and_cannot_repeat(tmp_path):
    service=_service(tmp_path)
    service.archive_asset(asset_id='asset-1',request_id='archive-1')
    with pytest.raises(ValueError,match='already archived'):
        service.archive_asset(asset_id='asset-1',request_id='archive-2')
    with service.database.read_connection() as connection:
        assert connection.execute("SELECT COUNT(*) n FROM event_identity WHERE event_type='INVENTORY_ASSET_ARCHIVED'").fetchone()['n']==1


def test_archived_asset_cannot_be_adjusted(tmp_path):
    service=_service(tmp_path); service.archive_asset(asset_id='asset-1',request_id='archive-1')
    with pytest.raises(ValueError,match='Archived inventory cannot be adjusted'):
        service.adjust_asset(asset_id='asset-1',quantity_delta=1,cost_delta_minor=0,request_id='adjust-archived')