import pytest

from market_intelligence.warehouse_migrations import (
    WAREHOUSE_MIGRATION_0001_NOOP,
    WAREHOUSE_SCHEMA_ONE,
    WAREHOUSE_SCHEMA_ZERO,
    WarehouseMigration,
    get_warehouse_migration,
    latest_warehouse_schema_version,
    list_warehouse_migrations,
)


def test_noop_migration_has_deterministic_metadata() -> None:
    migration = WAREHOUSE_MIGRATION_0001_NOOP

    assert migration.migration_id == 'warehouse-0001-noop-baseline'
    assert migration.sequence == 1
    assert migration.source_schema_version == WAREHOUSE_SCHEMA_ZERO
    assert migration.target_schema_version == WAREHOUSE_SCHEMA_ONE
    assert migration.metadata['build'] == '700Z'


def test_noop_migration_contains_no_sql_or_write_behavior() -> None:
    migration = WAREHOUSE_MIGRATION_0001_NOOP

    assert migration.is_noop is True
    assert migration.sql_statements == ()
    assert migration.metadata['provider_execution'] == 'forbidden'
    assert migration.metadata['product_registry_mutation'] == 'forbidden'


def test_migration_registry_is_tuple_based_and_ordered() -> None:
    migrations = list_warehouse_migrations()

    assert migrations == (WAREHOUSE_MIGRATION_0001_NOOP,)
    assert get_warehouse_migration('warehouse-0001-noop-baseline') == WAREHOUSE_MIGRATION_0001_NOOP
    assert get_warehouse_migration('missing') is None
    assert latest_warehouse_schema_version() == WAREHOUSE_SCHEMA_ONE


def test_build700z_rejects_sql_statements() -> None:
    with pytest.raises(ValueError, match='must not contain SQL statements'):
        WarehouseMigration(
            migration_id='unsafe-sql',
            sequence=2,
            source_schema_version=WAREHOUSE_SCHEMA_ONE,
            target_schema_version='market-intelligence-warehouse:2',
            description='Unsafe executable migration.',
            sql_statements=('CREATE TABLE market_observations (id TEXT)',),
        )


def test_migration_metadata_is_immutable() -> None:
    migration = WAREHOUSE_MIGRATION_0001_NOOP

    with pytest.raises(TypeError):
        migration.metadata['build'] = 'changed'  # type: ignore[index]
