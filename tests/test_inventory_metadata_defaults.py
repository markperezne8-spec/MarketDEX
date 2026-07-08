from services.inventory_app_service import InventoryAppService


def test_new_asset_has_empty_metadata_defaults(tmp_path):
    service = InventoryAppService(tmp_path / 'marketdex.sqlite3')
    service.add_asset(asset_id='asset-1', asset_name='Inventory Item', asset_type='SEALED', quantity=1, total_cost_minor=10000, request_id='add-1')
    detail = service.get_asset_detail('asset-1')
    assert detail['purchase_date'] == ''
    assert detail['purchase_source'] == ''
    assert detail['storage_location'] == ''
    assert detail['notes'] == ''
