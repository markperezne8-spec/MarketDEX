import sqlite3

import pytest

from core.database_manager import DatabaseManager, RUNTIME_SCHEMA_VERSION
from core.schema import SCHEMA_VERSION
from services.product_registry_service import ProductRegistryService


def test_product_registry_tables_are_owned_by_canonical_schema(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'
    database = DatabaseManager(path)
    database.initialize()

    with database.read_connection() as connection:
        tables = {row['name'] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        version = connection.execute('SELECT schema_version FROM schema_metadata ORDER BY rowid DESC LIMIT 1').fetchone()['schema_version']

    assert SCHEMA_VERSION == 24
    assert RUNTIME_SCHEMA_VERSION == 25
    assert version == RUNTIME_SCHEMA_VERSION
    assert {'products', 'product_aliases', 'product_registration_history', 'product_alias_history'} <= tables


def test_product_registry_uses_canonical_runtime_database_and_reconstructs_after_restart(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'
    service = ProductRegistryService(path)
    product_id = service.register('SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare', 'CAP005-REGISTER-001')
    service.add_alias(product_id, 'Charizard EX 125/197', 'CAP005-ALIAS-001')

    restarted = ProductRegistryService(path)

    assert restarted.resolve_alias('charizard ex 125 197') == product_id
    assert restarted.register('SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare', 'CAP005-REGISTER-001') == product_id
    with restarted.database.read_connection() as connection:
        assert connection.execute('SELECT COUNT(*) n FROM products WHERE product_id=?', (product_id,)).fetchone()['n'] == 1
        assert connection.execute('SELECT COUNT(*) n FROM product_registration_history WHERE product_id=?', (product_id,)).fetchone()['n'] == 1
        assert connection.execute("SELECT verification_result FROM audit_events WHERE authority_type='PRODUCT_REGISTRY' AND authority_id=?", (product_id,)).fetchone()['verification_result'] == 'VERIFIED'


def test_product_registry_blocks_duplicate_identity_and_alias_collision(tmp_path):
    service = ProductRegistryService(tmp_path / 'marketdex.sqlite3')
    first = service.register('SINGLE', 'Pikachu', 'Base Set', '58/102', 'Common', 'CAP005-REGISTER-PIKACHU')
    second = service.register('SEALED', 'Base Set Booster Pack', 'Base Set', None, 'Unlimited', 'CAP005-REGISTER-PACK')
    service.add_alias(first, 'Pikachu 58/102', 'CAP005-ALIAS-PIKACHU')

    with pytest.raises(ValueError, match='duplicate normalized identity key'):
        service.register('SINGLE', 'PIKACHU', 'BASE SET', '58 102', 'COMMON', 'CAP005-DUPLICATE')
    with pytest.raises(ValueError, match='alias collision'):
        service.add_alias(second, 'PIKACHU 58 102', 'CAP005-ALIAS-COLLISION')


def test_product_registry_history_is_append_only_under_canonical_schema(tmp_path):
    service = ProductRegistryService(tmp_path / 'marketdex.sqlite3')
    product_id = service.register('SEALED', 'Elite Trainer Box', 'Obsidian Flames', None, 'Standard', 'CAP005-REGISTER-ETB')

    with pytest.raises(sqlite3.IntegrityError, match='append-only'):
        with service.database.transaction() as connection:
            connection.execute('UPDATE product_registration_history SET resulting_state=? WHERE product_id=?', ('CHANGED', product_id))
