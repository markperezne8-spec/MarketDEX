from ui.inventory_marketplace_listing_preparation_feature import marketplace_listing_package


def test_listing_package_title_is_deterministic():
    row = {'asset_id': 'asset-1', 'asset_name': 'Chaos Rising ETB', 'asset_type': 'SEALED', 'quantity': 1, 'total_cost_minor': 6500}
    plan = {'marketplace': 'eBay', 'target_sale_price_minor': 10200}
    result = marketplace_listing_package(row, plan)
    assert 'TITLE: Chaos Rising ETB | SEALED' in result['lines']
