from ui.inventory_marketplace_listing_preparation_feature import marketplace_listing_package


def row(quantity=1, cost=10000):
    return {'asset_id': 'asset-1', 'asset_name': 'Test ETB', 'asset_type': 'SEALED', 'quantity': quantity, 'total_cost_minor': cost}


def plan(marketplace='eBay', price=15750):
    return {'marketplace': marketplace, 'target_sale_price_minor': price}


def test_preparation_decision_matrix():
    assert marketplace_listing_package(row(), plan())['prepared'] is True
    assert marketplace_listing_package(row(quantity=0), plan())['prepared'] is False
    assert marketplace_listing_package(row(), plan(marketplace=''))['prepared'] is False
    assert marketplace_listing_package(row(), plan(price=0))['prepared'] is False
    assert marketplace_listing_package(row(cost=20000), plan(price=10000))['prepared'] is False
