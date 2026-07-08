from ui.inventory_marketplace_listing_preparation_feature import marketplace_listing_package


def test_listing_package_preserves_saved_target_price():
    row = {'asset_id': 'asset-1', 'asset_name': 'Test ETB', 'asset_type': 'SEALED', 'quantity': 1, 'total_cost_minor': 6500}
    plan = {'marketplace': 'eBay', 'target_sale_price_minor': 10299}
    result = marketplace_listing_package(row, plan)
    assert 'TARGET PRICE: $102.99' in result['lines']
