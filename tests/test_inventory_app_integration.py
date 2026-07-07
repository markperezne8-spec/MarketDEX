import pytest
from core.event_repository import ReplayRejected
from services.inventory_app_service import InventoryAppService


def test_add_asset_projects_into_visible_inventory(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1',asset_name='Mega Evolution ETB',asset_type='SEALED',quantity=2,total_cost_minor=13000,request_id='request-1')
    assert service.list_inventory()==[{'asset_id':'asset-1','asset_name':'Mega Evolution ETB','asset_type':'SEALED','quantity':2,'total_cost_minor':13000}]
    with service.database.read_connection() as c:
        assert c.execute("SELECT COUNT(*) n FROM inventory_history WHERE asset_id='asset-1'").fetchone()['n']==1
        assert c.execute("SELECT verification_result FROM audit_events WHERE authority_id='asset-1'").fetchone()['verification_result']=='VERIFIED'


def test_add_asset_request_is_exactly_once(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1',asset_name='Card',asset_type='SINGLE',quantity=1,total_cost_minor=500,request_id='request-1')
    with pytest.raises(ReplayRejected):
        service.add_asset(asset_id='asset-2',asset_name='Other Card',asset_type='SINGLE',quantity=1,total_cost_minor=600,request_id='request-1')
    assert len(service.list_inventory())==1


def test_list_inventory_is_read_only(tmp_path):
    service=InventoryAppService(tmp_path/'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1',asset_name='Card',asset_type='SINGLE',quantity=1,total_cost_minor=500,request_id='request-1')
    before=service.list_inventory(); after=service.list_inventory(); assert before==after
