from pathlib import Path

from core.database_manager import DatabaseManager
from core.event_repository import EventRepository
from services.marketplace_lifecycle_service import MarketplaceLifecycleService


def test_operator_recorded_listed_outcome_uses_existing_append_only_publication_authority(tmp_path):
    database = DatabaseManager(tmp_path / 'marketdex.sqlite3')
    database.initialize()
    with database.transaction() as connection:
        connection.execute(
            "INSERT INTO assets(asset_id,asset_name,asset_type,state,created_event_id,created_at) VALUES(?,?,?,?,?,?)",
            ('ASSET-1', 'Charizard ex', 'Single', 'IN PROGRESS', 'EV-SEED', '2026-07-08T00:00:00+00:00'),
        )
        connection.execute(
            "INSERT INTO inventory_authority(asset_id,quantity,total_cost_minor,last_event_id,verified_at) VALUES(?,?,?,?,?)",
            ('ASSET-1', 2, 1000, 'EV-SEED', '2026-07-08T00:00:00+00:00'),
        )

    lifecycle = MarketplaceLifecycleService(database, EventRepository())
    event_id = lifecycle.list_publication(
        request_id='OPERATOR-LISTED-1',
        allocation_id='ALLOC-OPERATOR-1',
        asset_id='ASSET-1',
        marketplace='eBay',
        requested_allocation_quantity=2,
        publication_reference='EBAY-LISTING-123',
        publication_identity='OPERATOR-REF-eBay-EBAY-LISTING-123',
        evidence_type='OPERATOR_RECORDED_MARKETPLACE_OUTCOME',
        evidence_reference='EBAY-LISTING-123',
        evidence_complete=True,
        intent='LISTED',
    )

    with database.read_connection() as connection:
        allocation = connection.execute(
            'SELECT * FROM marketplace_publication_allocations WHERE allocation_id=?', ('ALLOC-OPERATOR-1',)
        ).fetchone()
        history = connection.execute(
            "SELECT * FROM publication_lifecycle_events WHERE allocation_id=? AND event_type='LISTED'",
            ('ALLOC-OPERATOR-1',),
        ).fetchone()
        inventory = connection.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?', ('ASSET-1',)).fetchone()
        audit = connection.execute(
            "SELECT * FROM audit_events WHERE event_id=? AND authority_type='LISTED' AND verification_result='VERIFIED'",
            (event_id,),
        ).fetchone()

    assert allocation['state'] == 'ACTIVE'
    assert allocation['publication_reference'] == 'EBAY-LISTING-123'
    assert history['evidence_type'] == 'OPERATOR_RECORDED_MARKETPLACE_OUTCOME'
    assert inventory['quantity'] == 2
    assert audit is not None


def test_desktop_connects_operator_outcome_after_completed_package_queue():
    launcher = Path('launcher.py').read_text(encoding='utf-8')
    viewport = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')
    queue = Path('ui/inventory_completed_listing_package_queue_feature.py').read_text(encoding='utf-8')
    feature = Path('ui/inventory_listing_execution_history_feature.py').read_text(encoding='utf-8')

    assert launcher.index('install_inventory_completed_listing_package_queue_feature(window)') < launcher.index(
        'install_inventory_listing_execution_history_feature(window)'
    )
    assert "'inventory_listing_execution_history'" in viewport
    assert "marketplace_publication_allocations WHERE state='ACTIVE'" in queue
    assert 'OPERATOR_RECORDED_MARKETPLACE_OUTCOME' in feature
    assert "intent='LISTED'" in feature
    assert 'publish' not in feature.lower() or 'list_publication' in feature
