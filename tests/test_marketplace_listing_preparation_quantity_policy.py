from ui.inventory_marketplace_listing_preparation_feature import marketplace_listing_package


def test_listing_package_displays_active_quantity():
    row = {'asset_id': 'asset-1', 'asset_name': 'Test Pack', 'asset_type': 'SEALED', 'quantity': 7, 'total_cost_minor': 3500}
    plan = {'marketplace': 'TCGplayer', 'target_sale_price_minor': 7000}
    result = marketplace_listing_package(row, plan)
    assert 'QUANTITY: 7' in result['lines']


def test_zero_quantity_blocks_package():
    row = {'asset_id': 'asset-1', 'asset_name': 'Test Pack', 'asset_type': 'SEALED', 'quantity': 0, 'total_cost_minor': 3500}
    plan = {'marketplace': 'TCGplayer', 'target_sale_price_minor': 7000}
    assert marketplace_listing_package(row, plan)['prepared'] is False
