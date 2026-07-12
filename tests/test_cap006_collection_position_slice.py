import pytest

from core.database_manager import DatabaseManager
from services.collection_position_service import CollectionPositionService


def _seed(path):
    database = DatabaseManager(path)
    database.initialize()
    with database.transaction() as connection:
        connection.execute("INSERT INTO assets VALUES ('asset-2','Pikachu','CARD','COMPLETED','event-asset-2','2026-01-01')")
        connection.execute("INSERT INTO assets VALUES ('asset-1','Charizard','CARD','COMPLETED','event-asset-1','2026-01-01')")
        connection.execute("INSERT INTO products VALUES ('product-2','SINGLE','Pikachu ex','pikachu ex','Surging Sparks','057/191','', 'REGISTERED','event-product-2','2026-01-01')")
        connection.execute("INSERT INTO products VALUES ('product-1','SINGLE','Charizard ex','charizard ex','Obsidian Flames','125/197','', 'REGISTERED','event-product-1','2026-01-01')")
        connection.execute("INSERT INTO inventory_authority VALUES ('asset-2',1,500,'event-inv-2','2026-01-01')")
        connection.execute("INSERT INTO inventory_authority VALUES ('asset-1',2,1000,'event-inv-1','2026-01-01')")
        connection.execute("INSERT INTO inventory_business_details VALUES ('asset-2','2026-01-03','Trade','Display Case','', 'event-details-2','2026-01-03')")
        connection.execute("INSERT INTO inventory_business_details VALUES ('asset-1','2026-01-02','Local Shop','Binder A','', 'event-details-1','2026-01-02')")
        connection.execute("INSERT INTO inventory_product_links VALUES ('link-2','asset-2','product-2','LINKED','event-link-2','2026-01-03')")
        connection.execute("INSERT INTO inventory_product_links VALUES ('link-1','asset-1','product-1','LINKED','event-link-1','2026-01-02')")


def _authority_counts(service):
    tables = (
        'assets',
        'products',
        'inventory_authority',
        'inventory_business_details',
        'inventory_product_links',
    )
    with service.database.read_connection() as connection:
        return {
            table: connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            for table in tables
        }


def test_collection_position_projection_is_deterministic_restart_safe_and_read_only(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'
    _seed(path)
    service = CollectionPositionService(path)
    before = _authority_counts(service)

    first = service.list_positions()
    restarted = CollectionPositionService(path).list_positions()

    assert first == restarted
    assert [position.canonical_name for position in first] == ['Charizard ex', 'Pikachu ex']
    assert first[0].quantity == 2
    assert first[0].storage_location == 'Binder A'
    assert all(position.condition_grade is None for position in first)
    assert all(position.collector_intent is None for position in first)
    assert _authority_counts(service) == before


@pytest.mark.parametrize(
    ('query', 'expected_asset_id'),
    (
        ('CHARIZARD', 'asset-1'),
        ('product-1', 'asset-1'),
        ('asset-1', 'asset-1'),
        ('binder a', 'asset-1'),
        ('display case', 'asset-2'),
    ),
)
def test_collection_position_search_uses_only_approved_projection_fields(tmp_path, query, expected_asset_id):
    path = tmp_path / 'marketdex.sqlite3'
    _seed(path)

    results = CollectionPositionService(path).list_positions(query)

    assert [position.asset_id for position in results] == [expected_asset_id]
    assert all(position.condition_grade is None for position in results)
    assert all(position.collector_intent is None for position in results)


def test_collection_position_limit_is_bounded_and_applied(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'
    _seed(path)
    service = CollectionPositionService(path)

    assert len(service.list_positions(limit=1)) == 1
    assert len(service.list_positions(limit='2')) == 2

    for invalid_limit in (0, 501, 'not-an-integer', None):
        with pytest.raises(ValueError):
            service.list_positions(limit=invalid_limit)


def test_collection_position_empty_and_unmatched_queries_fail_safely(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'
    service = CollectionPositionService(path)
    assert service.list_positions() == ()
    assert service.list_positions('missing') == ()
