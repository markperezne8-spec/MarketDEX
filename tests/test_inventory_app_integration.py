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


def test_tcg_inventory_details_persist_and_are_listed(tmp_path):
    database_path = tmp_path / 'marketdex.sqlite3'
    service = InventoryAppService(database_path)
    service.add_asset(asset_id='asset-1', asset_name='Charizard ex 199/165', asset_type='SINGLE', quantity=1, total_cost_minor=12000, request_id='request-1')
    service.update_business_details(asset_id='asset-1', storage_location='Binder A', notes='Centering checked', request_id='detail-1')
    service.update_tcg_details(asset_id='asset-1', product_name='Charizard ex 199/165', set_name='151', item_condition='Near Mint', market_price_minor=18500, request_id='tcg-1')
    reopened = InventoryAppService(database_path)
    row = reopened.list_inventory(include_details=True)[0]
    detail = reopened.get_asset_detail('asset-1')
    assert row['set_name'] == '151'
    assert row['item_condition'] == 'Near Mint'
    assert row['market_price_minor'] == 18500
    assert row['storage_location'] == 'Binder A'
    assert row['notes'] == 'Centering checked'
    assert detail['product_name'] == 'Charizard ex 199/165'


def test_inventory_edit_search_filter_totals_delete_and_persistence(tmp_path):
    database_path = tmp_path / 'marketdex.sqlite3'; service = InventoryAppService(database_path)
    service.add_asset(asset_id='asset-1', asset_name='Charizard ex', asset_type='SINGLE', quantity=1, total_cost_minor=10000, request_id='add-1')
    service.update_asset(asset_id='asset-1', asset_name='Charizard ex 199/165', asset_type='SINGLE', quantity=2, total_cost_minor=20000, product_name='Charizard ex 199/165', set_name='151', item_condition='Near Mint', market_price_minor=17500, storage_location='Binder A', notes='For sale', request_id='edit-1')
    reopened = InventoryAppService(database_path)
    rows = reopened.list_inventory(search_text='binder a', item_condition='Near Mint', include_details=True)
    assert [row['asset_name'] for row in rows] == ['Charizard ex 199/165']
    assert reopened.summarize_inventory(rows) == {'asset_count':1,'total_units':2,'total_cost_minor':20000,'total_market_value_minor':35000,'estimated_profit_minor':15000}
    assert reopened.delete_asset(asset_id='asset-1', request_id='delete-1')['state'] == 'CANCELLED'
    assert reopened.list_inventory(include_details=True) == []
    assert reopened.list_archived_inventory(include_details=True)[0]['storage_location'] == 'Binder A'
