import pytest

from services.inventory_app_service import InventoryAppService


def _service(tmp_path):
    service = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1', asset_name='Charizard ex', asset_type='SINGLE', quantity=2, total_cost_minor=12000, request_id='add-1')
    service.add_asset(asset_id='asset-2', asset_name='Chaos Rising ETB', asset_type='SEALED', quantity=1, total_cost_minor=5000, request_id='add-2')
    service.add_asset(asset_id='asset-3', asset_name='Pikachu', asset_type='SINGLE', quantity=3, total_cost_minor=9000, request_id='add-3')
    return service


def test_listing_details_persist_filters_and_queue_after_reopen(tmp_path):
    service = _service(tmp_path)
    service.update_listing_details(asset_id='asset-1', listing_status='Ready to List', marketplace='eBay', asking_price_minor=18500, sku='CHAR-151-NM', storage_location='Binder A', listing_title='Charizard ex 199/165 Near Mint', listing_notes='Photograph front and back', request_id='listing-1')
    service.update_listing_details(asset_id='asset-2', listing_status='Listed', marketplace='TCGplayer', asking_price_minor=27500, sku='ETB-CR-001', storage_location='Shelf 2', listing_title='Chaos Rising Elite Trainer Box', listing_notes='Sealed', request_id='listing-2')
    service.update_listing_details(asset_id='asset-3', listing_status='Ready to List', marketplace='TCGplayer', asking_price_minor=9500, sku='PIKA-001', storage_location='Binder B', listing_title='Pikachu Near Mint', listing_notes='Ready for photos', request_id='listing-3')
    reopened = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    detail = reopened.get_asset_detail('asset-1')
    assert detail['listing_status'] == 'Ready to List'
    assert detail['marketplace'] == 'eBay'
    assert detail['asking_price_minor'] == 18500
    assert detail['sku'] == 'CHAR-151-NM'
    assert detail['storage_location'] == 'Binder A'
    assert detail['listing_title'] == 'Charizard ex 199/165 Near Mint'
    assert detail['listing_notes'] == 'Photograph front and back'
    queue = reopened.list_inventory(include_details=True, listing_queue=True)
    assert [row['asset_id'] for row in queue] == ['asset-1', 'asset-3']
    ebay_ready = reopened.list_inventory(include_details=True, listing_status='Ready to List', marketplace='eBay')
    assert [row['asset_id'] for row in ebay_ready] == ['asset-1']
    tcg_listed = reopened.list_inventory(include_details=True, listing_status='Listed', marketplace='TCGplayer')
    assert [row['asset_id'] for row in tcg_listed] == ['asset-2']


def test_existing_inventory_defaults_to_not_listed_and_validation_is_persisted(tmp_path):
    service = _service(tmp_path)
    assert service.get_asset_detail('asset-1')['listing_status'] == 'Not Listed'
    with pytest.raises(ValueError, match='valid listing status'):
        service.update_listing_details(asset_id='asset-1', listing_status='Unknown', request_id='bad-status')
    with pytest.raises(ValueError, match='negative'):
        service.update_listing_details(asset_id='asset-1', asking_price_minor=-1, request_id='bad-price')
    with pytest.raises(ValueError, match='listing detail change'):
        service.update_listing_details(asset_id='asset-1', request_id='no-change')
