from core.database_manager import DatabaseManager
from core.listing_plan_repository import ListingPlanRepository


def test_listing_plan_persists_and_updates_by_asset(tmp_path):
    database = DatabaseManager(tmp_path / 'marketdex.db')
    database.initialize()
    repository = ListingPlanRepository(database)

    first = repository.save('asset-1', 'eBay', 15750, 20.0, 500, 100, 20.0)
    assert first['asset_id'] == 'asset-1'
    assert first['target_sale_price_minor'] == 15750
    assert first['marketplace'] == 'eBay'

    updated = repository.save('asset-1', 'TCGplayer', 16000, 13.0, 550, 125, 25.0)
    assert updated['plan_id'] == first['plan_id']
    assert updated['marketplace'] == 'TCGplayer'
    assert updated['target_sale_price_minor'] == 16000
    assert len(repository.list_all()) == 1


def test_listing_plan_survives_repository_restart(tmp_path):
    path = tmp_path / 'marketdex.db'
    database = DatabaseManager(path)
    database.initialize()
    ListingPlanRepository(database).save('asset-9', 'eBay', 13250, 20.0, 500, 100, 20.0)

    reopened = DatabaseManager(path)
    reopened.initialize()
    plan = ListingPlanRepository(reopened).get('asset-9')
    assert plan['shipping_minor'] == 500
    assert plan['packaging_minor'] == 100
    assert plan['target_roi_percent'] == 20.0
