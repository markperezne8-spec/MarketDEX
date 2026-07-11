import sqlite3

import pytest

from core.database_manager import DatabaseManager
from services.inventory_product_link_service import InventoryProductLinkService
from services.marketplace_listing_readiness_service import MarketplaceListingReadinessService


def test_product_link_and_listing_readiness_are_owned_by_canonical_schema(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'
    database = DatabaseManager(path)
    database.initialize()

    with database.read_connection() as connection:
        tables = {row['name'] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        triggers = {row['name'] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}

    assert {
        'inventory_product_links',
        'inventory_product_link_history',
        'marketplace_listing_identities',
        'marketplace_listing_identity_history',
        'publication_readiness_history',
    } <= tables
    assert {
        'inventory_product_link_history_no_update',
        'inventory_product_link_history_no_delete',
        'marketplace_listing_identity_history_no_update',
        'marketplace_listing_identity_history_no_delete',
        'publication_readiness_history_no_update',
        'publication_readiness_history_no_delete',
    } <= triggers


def test_product_link_and_listing_readiness_reconstruct_through_one_runtime_database(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'

    assert InventoryProductLinkService(path).run_acceptance()['passed'] == 12
    assert MarketplaceListingReadinessService(path).run_acceptance()['passed'] == 12

    with DatabaseManager(path).read_connection() as connection:
        link = connection.execute('SELECT inventory_product_link_id FROM inventory_product_links').fetchone()
        listing = connection.execute('SELECT listing_identity_id FROM marketplace_listing_identities').fetchone()
        assert link is not None
        assert listing is not None

    with pytest.raises(sqlite3.IntegrityError, match='append-only'):
        with DatabaseManager(path).transaction() as connection:
            connection.execute('DELETE FROM inventory_product_link_history')

    assert InventoryProductLinkService(path).verify()['passed'] == 12
    assert MarketplaceListingReadinessService(path).verify()['passed'] == 12
