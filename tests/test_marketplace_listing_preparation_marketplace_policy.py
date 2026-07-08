from ui.inventory_marketplace_listing_preparation_feature import marketplace_listing_package


def test_listing_package_preserves_saved_marketplace():
    row = {'asset_id': 'asset-1', 'asset_name': 'Test Card', 'asset_type': 'SINGLE', 'quantity': 1, 'total_cost_minor': 1000}
    plan = {'marketplace': 'TCGplayer', 'target_sale_price_minor': 2000}
    result = marketplace_listing_package(row, plan)
    assert 'MARKETPLACE: TCGplayer' in result['lines']


def test_blank_marketplace_blocks_package():
    row = {'asset_id': 'asset-1', 'asset_name': 'Test Card', 'asset_type': 'SINGLE', 'quantity': 1, 'total_cost_minor': 1000}
    plan = {'marketplace': '', 'target_sale_price_minor': 2000}
    assert marketplace_listing_package(row, plan)['prepared'] is False
