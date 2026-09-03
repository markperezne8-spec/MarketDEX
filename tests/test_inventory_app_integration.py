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


def test_typed_inventory_adjustments_persist_activity_and_block_negative_quantity(tmp_path):
    database_path=tmp_path/'marketdex.sqlite3'; service=InventoryAppService(database_path)
    service.add_asset(asset_id='asset-1',asset_name='Card',asset_type='SINGLE',quantity=2,total_cost_minor=1000,request_id='add-1')
    service.record_adjustment(asset_id='asset-1',adjustment_type='ADD_STOCK',quantity_delta=3,reason='Bought local collection',request_id='adjust-1')
    service.record_adjustment(asset_id='asset-1',adjustment_type='SOLD_OUTSIDE_PLATFORM',quantity_delta=-1,reason='Cash sale at show',request_id='adjust-2')
    reopened=InventoryAppService(database_path); assert reopened.get_asset_detail('asset-1')['quantity']==4; assert reopened.summarize_inventory(reopened.list_inventory())['total_units']==4
    history=reopened.list_item_activity('asset-1'); assert [(row['adjustment_type'],row['quantity_delta'],row['reason'],row['resulting_quantity']) for row in history]==[('SOLD_OUTSIDE_PLATFORM',-1,'Cash sale at show',4),('ADD_STOCK',3,'Bought local collection',5)]
    with pytest.raises(ValueError,match='negative'): reopened.record_adjustment(asset_id='asset-1',adjustment_type='DAMAGED',quantity_delta=-5,reason='Water damage',request_id='adjust-3')
    with pytest.raises(ValueError,match='reason'): reopened.record_adjustment(asset_id='asset-1',adjustment_type='CORRECTION',quantity_delta=1,reason='',request_id='adjust-4')



def test_listing_details_persist_filters_and_queue_after_reopen(tmp_path):
    service = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1', asset_name='Charizard ex', asset_type='SINGLE', quantity=2, total_cost_minor=12000, request_id='add-1')
    service.add_asset(asset_id='asset-2', asset_name='Chaos Rising ETB', asset_type='SEALED', quantity=1, total_cost_minor=5000, request_id='add-2')
    service.add_asset(asset_id='asset-3', asset_name='Pikachu', asset_type='SINGLE', quantity=3, total_cost_minor=9000, request_id='add-3')
    service.update_tcg_details(asset_id='asset-1', product_name='Charizard ex', set_name='151', item_condition='Near Mint', market_price_minor=18500, request_id='tcg-1')
    service.update_tcg_details(asset_id='asset-3', product_name='Pikachu', set_name='151', item_condition='Near Mint', market_price_minor=9500, request_id='tcg-3')
    service.update_listing_details(asset_id='asset-1', listing_status='Ready to List', marketplace='eBay', asking_price_minor=18500, sku='CHAR-151-NM', storage_location='Binder A', listing_title='Charizard ex 199/165 Near Mint', listing_notes='Photograph front and back', photos_ready='Ready', photo_reference='charizard-front-back.jpg', request_id='listing-1')
    service.update_listing_details(asset_id='asset-2', listing_status='Listed', marketplace='TCGplayer', asking_price_minor=27500, sku='ETB-CR-001', storage_location='Shelf 2', listing_title='Chaos Rising Elite Trainer Box', listing_notes='Sealed', request_id='listing-2')
    service.update_listing_details(asset_id='asset-3', listing_status='Ready to List', marketplace='TCGplayer', asking_price_minor=9500, sku='PIKA-001', storage_location='Binder B', listing_title='Pikachu Near Mint', listing_notes='Ready for photos', photos_ready='Ready', photo_reference='pikachu-front-back.jpg', request_id='listing-3')
    reopened = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    detail = reopened.get_asset_detail('asset-1')
    assert detail['listing_status'] == 'Ready to List'
    assert detail['marketplace'] == 'eBay'
    assert detail['asking_price_minor'] == 18500
    assert detail['sku'] == 'CHAR-151-NM'
    assert detail['storage_location'] == 'Binder A'
    assert detail['listing_title'] == 'Charizard ex 199/165 Near Mint'
    assert detail['listing_notes'] == 'Photograph front and back'
    assert detail['photos_ready'] == 'Ready'
    assert detail['photo_reference'] == 'charizard-front-back.jpg'
    assert [row['asset_id'] for row in reopened.list_inventory(include_details=True, listing_queue=True)] == ['asset-1', 'asset-3']
    assert [row['asset_id'] for row in reopened.list_inventory(include_details=True, listing_status='Ready to List', marketplace='eBay')] == ['asset-1']
    assert [row['asset_id'] for row in reopened.list_inventory(include_details=True, listing_status='Listed', marketplace='TCGplayer')] == ['asset-2']


def test_existing_inventory_listing_defaults_and_validation(tmp_path):
    service = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1', asset_name='Charizard ex', asset_type='SINGLE', quantity=2, total_cost_minor=12000, request_id='add-1')
    assert service.get_asset_detail('asset-1')['listing_status'] == 'Not Listed'
    with pytest.raises(ValueError, match='valid listing status'):
        service.update_listing_details(asset_id='asset-1', listing_status='Unknown', request_id='bad-status')
    with pytest.raises(ValueError, match='negative'):
        service.update_listing_details(asset_id='asset-1', asking_price_minor=-1, request_id='bad-price')
    with pytest.raises(ValueError, match='listing detail change'):
        service.update_listing_details(asset_id='asset-1', request_id='no-change')



def test_listing_readiness_blocks_incomplete_items_and_persists_after_completion(tmp_path):
    database_path = tmp_path / 'marketdex.sqlite3'
    service = InventoryAppService(database_path)
    service.add_asset(asset_id='asset-1', asset_name='Charizard ex', asset_type='SINGLE', quantity=1, total_cost_minor=12000, request_id='add-1')

    initial = service.get_listing_readiness('asset-1')
    assert initial['readiness_state'] == 'BLOCKED'
    assert initial['readiness_blocker_count'] == 7
    assert 'Condition must be evaluated' in initial['readiness_blockers']
    assert 'Marketplace is not selected' in initial['readiness_blockers']
    assert 'Asking price must be greater than $0.00' in initial['readiness_blockers']
    assert 'Photo readiness is not evaluated' in initial['readiness_blockers']

    with pytest.raises(ValueError, match='Ready to List blocked:.*Marketplace is not selected'):
        service.update_listing_details(asset_id='asset-1', listing_status='Ready to List', request_id='ready-too-soon')

    with pytest.raises(ValueError, match='valid photo readiness value'):
        service.update_listing_details(asset_id='asset-1', photos_ready='Unknown', request_id='bad-photos')

    service.update_tcg_details(asset_id='asset-1', product_name='Charizard ex', set_name='151', item_condition='Near Mint', market_price_minor=18500, request_id='tcg-1')
    service.update_business_details(asset_id='asset-1', storage_location='Binder A', request_id='business-1')
    service.update_listing_details(asset_id='asset-1', listing_status='Ready to List', marketplace='eBay', asking_price_minor=18500, sku='CHAR-151-NM', storage_location='Binder A', listing_title='Charizard ex Near Mint', listing_notes='Front and back photos', photos_ready='Ready', photo_reference='charizard-front-back.jpg', request_id='listing-1')

    reopened = InventoryAppService(database_path)
    readiness = reopened.get_listing_readiness('asset-1')
    assert readiness == {'readiness_state': 'READY TO LIST', 'readiness_blockers': [], 'readiness_blocker_count': 0}
    assert reopened.get_asset_detail('asset-1')['listing_status'] == 'Ready to List'
    assert reopened.list_inventory(include_details=True)[0]['readiness_state'] == 'READY TO LIST'
