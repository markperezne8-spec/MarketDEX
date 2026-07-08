import pytest
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService


def _archived_service(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1',asset_name='Mistake ETB',asset_type='SINGLE',quantity=4,total_cost_minor=5000,request_id='seed-1')
    service.archive_asset(asset_id='asset-1',request_id='archive-1')
    return service


def test_archived_inventory_is_visible_in_archived_projection(tmp_path):
    service=_archived_service(tmp_path)
    assert service.list_inventory()==[]
    archived=service.list_archived_inventory()
    assert len(archived)==1
    assert archived[0]['asset_id']=='asset-1'
    assert archived[0]['state']=='CANCELLED'


def test_restore_returns_asset_to_active_inventory_without_mutating_history(tmp_path):
    service=_archived_service(tmp_path)
    with service.database.read_connection() as connection:
        before_history=connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n']
        before_movements=connection.execute('SELECT COUNT(*) n FROM inventory_movements').fetchone()['n']
    restored=service.restore_asset(asset_id='asset-1',request_id='restore-1')
    assert restored['state']=='COMPLETED'
    assert restored['quantity']==4
    assert restored['total_cost_minor']==5000
    assert [row['asset_id'] for row in service.list_inventory()]==['asset-1']
    assert service.list_archived_inventory()==[]
    with service.database.read_connection() as connection:
        assert connection.execute('SELECT COUNT(*) n FROM inventory_history').fetchone()['n']==before_history
        assert connection.execute('SELECT COUNT(*) n FROM inventory_movements').fetchone()['n']==before_movements
        assert connection.execute("SELECT COUNT(*) n FROM event_identity WHERE event_type='INVENTORY_ASSET_RESTORED'").fetchone()['n']==1
        assert connection.execute("SELECT COUNT(*) n FROM audit_events WHERE authority_type='INVENTORY_RESTORE' AND verification_result='VERIFIED'").fetchone()['n']==1


def test_restore_updates_active_mission_control_projection(tmp_path):
    service=_archived_service(tmp_path); mission=MissionControlService(tmp_path/'marketdex.sqlite3')
    before=mission.snapshot(); assert before['inventory_asset_count']==0
    service.restore_asset(asset_id='asset-1',request_id='restore-1')
    after=mission.snapshot(); assert after['inventory_asset_count']==1; assert after['inventory_units']==4; assert after['inventory_cost_minor']==5000


def test_active_asset_cannot_be_restored(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1',asset_name='Active',asset_type='SINGLE',quantity=1,total_cost_minor=100,request_id='seed-1')
    with pytest.raises(ValueError,match='Only archived inventory can be restored'):
        service.restore_asset(asset_id='asset-1',request_id='restore-1')


def test_restored_asset_cannot_be_restored_twice(tmp_path):
    service=_archived_service(tmp_path); service.restore_asset(asset_id='asset-1',request_id='restore-1')
    with pytest.raises(ValueError,match='Only archived inventory can be restored'):
        service.restore_asset(asset_id='asset-1',request_id='restore-2')
    with service.database.read_connection() as connection:
        assert connection.execute("SELECT COUNT(*) n FROM event_identity WHERE event_type='INVENTORY_ASSET_RESTORED'").fetchone()['n']==1