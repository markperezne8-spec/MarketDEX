from services.inventory_app_service import InventoryAppService
from services.inventory_csv_import_service import InventoryCsvImportService


def test_bulk_csv_import_persists_valid_rows_and_skips_invalid_rows(tmp_path):
    database_path = tmp_path / 'marketdex.sqlite3'
    service = InventoryAppService(database_path)
    service.add_asset(asset_id='existing', asset_name='Existing ETB', asset_type='SEALED', quantity=1, total_cost_minor=5000, request_id='existing-1')
    source = tmp_path / 'inventory.csv'
    source.write_text(
        'Item Name,Category,Quantity,Condition,Cost,Market Price,Storage Location,Set / Product,Notes,SKU\n'
        'Charizard ex,SINGLE,2,Near Mint,100.00,175.00,Binder A,151,For sale,CHAR-151\n'
        'Bad Card,SINGLE,nope,Near Mint,5.00,10.00,Binder B,Base,,BAD-1\n'
        'Sealed ETB,SEALED,1,Sealed,40.00,55.00,Shelf 2,Journey Together,,ETB-1\n',
        encoding='utf-8',
    )
    importer = InventoryCsvImportService(service)
    preview = importer.preview_csv(source)
    assert preview['total_rows'] == 3
    assert len(preview['valid_rows']) == 2
    assert preview['skipped_rows'] == 1
    result = importer.import_csv(source, 'import-1')
    assert result['imported_rows'] == 2
    assert result['skipped_rows'] == 1
    reopened = InventoryAppService(database_path)
    rows = reopened.list_inventory(include_details=True)
    assert {row['asset_name'] for row in rows} == {'Existing ETB', 'Charizard ex', 'Sealed ETB'}
    charizard = next(row for row in rows if row['asset_name'] == 'Charizard ex')
    assert charizard['set_name'] == '151'
    assert charizard['storage_location'] == 'Binder A'
    assert reopened.get_asset_detail(charizard['asset_id'])['sku'] == 'CHAR-151'
    assert reopened.summarize_inventory(rows)['total_market_value_minor'] == 40500
