import sqlite3

from core.runtime_database_migration import migrate_legacy_database_if_needed


def create_legacy_database(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute('CREATE TABLE assets(asset_id TEXT PRIMARY KEY, state TEXT NOT NULL)')
        connection.execute('CREATE TABLE inventory_authority(asset_id TEXT PRIMARY KEY, quantity INTEGER NOT NULL)')
        connection.execute("INSERT INTO assets VALUES('ASSET-LEGACY', 'COMPLETED')")
        connection.execute("INSERT INTO inventory_authority VALUES('ASSET-LEGACY', 1)")
        connection.commit()


def test_existing_nonempty_runtime_is_never_replaced_by_legacy_candidate(tmp_path):
    runtime = tmp_path / 'runtime' / 'marketdex.sqlite3'
    runtime.parent.mkdir(parents=True)
    with sqlite3.connect(runtime) as connection:
        connection.execute('CREATE TABLE operator_marker(value TEXT NOT NULL)')
        connection.execute("INSERT INTO operator_marker VALUES('KEEP-ME')")
        connection.commit()
    create_legacy_database(tmp_path / 'data' / 'm51_m55_acceptance.sqlite3')

    result = migrate_legacy_database_if_needed(runtime, tmp_path)

    assert result is None
    with sqlite3.connect(runtime) as connection:
        assert connection.execute('SELECT value FROM operator_marker').fetchone()[0] == 'KEEP-ME'


def test_missing_runtime_can_be_seeded_from_valid_legacy_inventory(tmp_path):
    runtime = tmp_path / 'runtime' / 'marketdex.sqlite3'
    legacy = tmp_path / 'data' / 'm51_m55_acceptance.sqlite3'
    create_legacy_database(legacy)

    result = migrate_legacy_database_if_needed(runtime, tmp_path)

    assert result == legacy
    with sqlite3.connect(runtime) as connection:
        assert connection.execute('SELECT quantity FROM inventory_authority WHERE asset_id=?', ('ASSET-LEGACY',)).fetchone()[0] == 1
