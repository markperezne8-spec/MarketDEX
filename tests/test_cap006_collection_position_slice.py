from core.database_manager import DatabaseManager
from services.collection_position_service import CollectionPositionService


def _seed(path):
    database = DatabaseManager(path)
    database.initialize()
    with database.transaction() as connection:
        connection.execute("INSERT INTO assets VALUES ('asset-1','Charizard','CARD','COMPLETED','event-asset','2026-01-01')")
        connection.execute("INSERT INTO products VALUES ('product-1','SINGLE','Charizard ex','charizard ex','Obsidian Flames','125/197','', 'REGISTERED','event-product','2026-01-01')")
        connection.execute("INSERT INTO inventory_authority VALUES ('asset-1',2,1000,'event-inv','2026-01-01')")
        connection.execute("INSERT INTO inventory_business_details VALUES ('asset-1','2026-01-02','Local Shop','Binder A','', 'event-details','2026-01-02')")
        connection.execute("INSERT INTO inventory_product_links VALUES ('link-1','asset-1','product-1','LINKED','event-link','2026-01-02')")


def test_collection_position_projection_is_deterministic_and_read_only(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'
    _seed(path)
    service = CollectionPositionService(path)
    first = service.list_positions()
    second = CollectionPositionService(path).list_positions('charizard')
    assert first == second
    assert first[0].quantity == 2
    assert first[0].storage_location == 'Binder A'
    assert first[0].condition_grade is None
    assert first[0].collector_intent is None
    with service.database.read_connection() as connection:
        assert connection.execute('SELECT COUNT(*) FROM inventory_product_links').fetchone()[0] == 1


def test_collection_position_empty_and_unmatched_queries_fail_safely(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'
    service = CollectionPositionService(path)
    assert service.list_positions() == ()
    assert service.list_positions('missing') == ()
