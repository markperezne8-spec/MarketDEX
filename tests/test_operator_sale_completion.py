from pathlib import Path

from composition.feature_catalog import CORE_DESKTOP_FEATURES
from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.marketplace_lifecycle_service import MarketplaceLifecycleService
from services.operator_sale_completion_service import OperatorSaleCompletionService


def seeded_database(tmp_path):
    database = DatabaseManager(tmp_path / 'marketdex.sqlite3'); database.initialize()
    with database.transaction() as connection:
        connection.execute("INSERT INTO assets(asset_id,asset_name,asset_type,state,created_event_id,created_at) VALUES(?,?,?,?,?,?)", ('ASSET-1','Charizard ex','Single','IN PROGRESS','EV-SEED','2026-07-08T00:00:00+00:00'))
        connection.execute("INSERT INTO inventory_authority(asset_id,quantity,total_cost_minor,last_event_id,verified_at) VALUES(?,?,?,?,?)", ('ASSET-1',2,1000,'EV-SEED','2026-07-08T00:00:00+00:00'))
    MarketplaceLifecycleService(database, EventRepository()).list_publication(request_id='LIST-1', allocation_id='ALLOC-1', asset_id='ASSET-1', marketplace='eBay', requested_allocation_quantity=2, publication_reference='EBAY-123', publication_identity='OPERATOR-REF-eBay-EBAY-123', evidence_type='OPERATOR_RECORDED_MARKETPLACE_OUTCOME', evidence_reference='EBAY-123', evidence_complete=True, intent='LISTED')
    return database


def test_operator_sale_completion_creates_one_sale_one_financial_event_and_one_inventory_decrement(tmp_path):
    database = seeded_database(tmp_path)
    OperatorSaleCompletionService(database).complete_sale(sale_request_id='SALE-REQ-1', conversion_request_id='SOLD-REQ-1', sale_id='SALE-1', allocation_id='ALLOC-1', sale_quantity=1, revenue_minor=2500, marketplace_fees_minor=325, shipping_minor=100, packaging_minor=25, evidence_reference='ORDER-99', intent='SOLD')
    with database.read_connection() as connection:
        sale = connection.execute("SELECT * FROM sales WHERE sale_id='SALE-1'").fetchone()
        inventory = connection.execute("SELECT quantity FROM inventory_authority WHERE asset_id='ASSET-1'").fetchone()
        financials = connection.execute("SELECT COUNT(*) n FROM sales_financial_history WHERE sale_id='SALE-1'").fetchone()['n']
        allocation = connection.execute("SELECT * FROM marketplace_publication_allocations WHERE allocation_id='ALLOC-1'").fetchone()
        sold = connection.execute("SELECT * FROM publication_lifecycle_events WHERE allocation_id='ALLOC-1' AND event_type='SOLD_CONVERSION'").fetchone()
    assert sale['state'] == 'COMPLETED'
    assert inventory['quantity'] == 1
    assert financials == 1
    assert allocation['consumed_quantity'] == 1
    assert allocation['state'] == 'ACTIVE'
    assert sold['sale_id'] == 'SALE-1'


def test_desktop_places_sale_completion_after_listing_history():
    launcher = Path('launcher.py').read_text(encoding='utf-8')
    viewport = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')
    feature = Path('ui/inventory_sale_completion_feature.py').read_text(encoding='utf-8')
    feature_ids = [definition.feature_id for definition in CORE_DESKTOP_FEATURES]

    assert 'install_inventory_' not in launcher
    assert feature_ids.index('inventory-listing-execution-history') < feature_ids.index(
        'inventory-sale-completion'
    )
    assert "'inventory-listing-execution-history'" in CORE_DESKTOP_FEATURES[
        feature_ids.index('inventory-sale-completion')
    ].depends_on
    assert "'inventory_sale_completion'" in viewport
    assert 'OperatorSaleCompletionService' in feature
    assert "intent='SOLD'" in feature
