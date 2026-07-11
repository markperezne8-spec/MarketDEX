import sqlite3

import pytest

from core.database_manager import DatabaseManager, RUNTIME_SCHEMA_VERSION
from services.inventory_product_link_service import InventoryProductLinkService


def test_cap005b_linkage_uses_runtime_schema_v25_and_survives_restart(tmp_path):
    database_path = tmp_path / 'marketdex.db'
    service = InventoryProductLinkService(database_path)
    product_id = service.ensure_acceptance_authority()
    before = service.quantities(product_id)
    link_id = service.link(service.ASSET if hasattr(service, 'ASSET') else 'AST-M35-CHARIZARD-001', product_id, 'CAP005B-LINK-001')
    after = service.quantities(product_id)

    restarted = InventoryProductLinkService(database_path)
    assert RUNTIME_SCHEMA_VERSION == 25
    assert before == (3, 3)
    assert after == before
    assert restarted.quantities(product_id) == (3, 3)
    assert restarted.link('AST-M35-CHARIZARD-001', product_id, 'CAP005B-LINK-001') == link_id


def test_cap005b_conflict_zero_mutation_history_and_audit(tmp_path):
    database_path = tmp_path / 'marketdex.db'
    service = InventoryProductLinkService(database_path)
    product_id = service.ensure_acceptance_authority()
    link_id = service.link('AST-M35-CHARIZARD-001', product_id, 'CAP005B-LINK-002')
    other_product = service._ensure_other_product()

    with pytest.raises(ValueError, match='conflicting product linkage'):
        service.link('AST-M35-CHARIZARD-001', other_product, 'CAP005B-CONFLICT-001')

    manager = DatabaseManager(database_path)
    with manager.read_connection() as connection:
        event_id = connection.execute(
            'SELECT created_event_id FROM inventory_product_links WHERE inventory_product_link_id=?',
            (link_id,),
        ).fetchone()['created_event_id']
        assert connection.execute('SELECT COUNT(*) n FROM inventory_history WHERE event_id=?', (event_id,)).fetchone()['n'] == 0
        assert connection.execute('SELECT COUNT(*) n FROM inventory_product_link_history WHERE inventory_product_link_id=?', (link_id,)).fetchone()['n'] == 1
        assert connection.execute(
            "SELECT COUNT(*) n FROM audit_events WHERE authority_type='INVENTORY_PRODUCT_LINK' AND authority_id=? AND verification_result='VERIFIED'",
            (link_id,),
        ).fetchone()['n'] == 1
        with pytest.raises(sqlite3.IntegrityError, match='append-only'):
            connection.execute('DELETE FROM inventory_product_link_history WHERE inventory_product_link_id=?', (link_id,))
