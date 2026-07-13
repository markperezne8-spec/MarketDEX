from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


WAREHOUSE_SCHEMA_ZERO = 'market-intelligence-warehouse:0'
WAREHOUSE_SCHEMA_ONE = 'market-intelligence-warehouse:1'


def _required_text(field_name: str, value: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f'{field_name} must not be empty')
    return normalized


@dataclass(frozen=True)
class WarehouseMigration:
    """Metadata-only warehouse migration definition.

    Build 700Z intentionally introduces no SQL execution, SQLite connection,
    migration runner, table creation, seed data, imports, or writes.
    """

    migration_id: str
    sequence: int
    source_schema_version: str
    target_schema_version: str
    description: str
    sql_statements: tuple[str, ...] = ()
    metadata: Mapping[str, str] = MappingProxyType({})

    def __post_init__(self) -> None:
        object.__setattr__(self, 'migration_id', _required_text('migration_id', self.migration_id))
        object.__setattr__(self, 'source_schema_version', _required_text('source_schema_version', self.source_schema_version))
        object.__setattr__(self, 'target_schema_version', _required_text('target_schema_version', self.target_schema_version))
        object.__setattr__(self, 'description', _required_text('description', self.description))
        if self.sequence < 1:
            raise ValueError('sequence must be positive')
        object.__setattr__(self, 'sql_statements', tuple(self.sql_statements))
        if self.sql_statements:
            raise ValueError('Build 700Z migration skeleton must not contain SQL statements')
        object.__setattr__(self, 'metadata', MappingProxyType(dict(self.metadata)))

    @property
    def is_noop(self) -> bool:
        return not self.sql_statements


WAREHOUSE_MIGRATION_0001_NOOP = WarehouseMigration(
    migration_id='warehouse-0001-noop-baseline',
    sequence=1,
    source_schema_version=WAREHOUSE_SCHEMA_ZERO,
    target_schema_version=WAREHOUSE_SCHEMA_ONE,
    description='No-op baseline marker for the future offline Market Intelligence warehouse schema.',
    metadata={
        'build': '700Z',
        'offline_only': 'true',
        'product_registry_mutation': 'forbidden',
        'provider_execution': 'forbidden',
    },
)


WAREHOUSE_MIGRATIONS: tuple[WarehouseMigration, ...] = (
    WAREHOUSE_MIGRATION_0001_NOOP,
)


def list_warehouse_migrations() -> tuple[WarehouseMigration, ...]:
    """Return known warehouse migrations in deterministic sequence order."""

    return tuple(sorted(WAREHOUSE_MIGRATIONS, key=lambda migration: migration.sequence))


def get_warehouse_migration(migration_id: str) -> WarehouseMigration | None:
    normalized_id = _required_text('migration_id', migration_id)
    for migration in WAREHOUSE_MIGRATIONS:
        if migration.migration_id == normalized_id:
            return migration
    return None


def latest_warehouse_schema_version() -> str:
    migrations = list_warehouse_migrations()
    if not migrations:
        return WAREHOUSE_SCHEMA_ZERO
    return migrations[-1].target_schema_version
