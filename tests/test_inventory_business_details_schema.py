from core.database_manager import DatabaseManager
from core.schema import SCHEMA_VERSION


def test_business_details_schema_is_upgrade_safe(tmp_path):
    path = tmp_path / 'marketdex.sqlite3'
    database = DatabaseManager(path)
    database.initialize()
    database.initialize()

    with database.read_connection() as connection:
        columns = {row['name'] for row in connection.execute('PRAGMA table_info(inventory_business_details)').fetchall()}
        version = connection.execute('SELECT schema_version FROM schema_metadata ORDER BY rowid DESC LIMIT 1').fetchone()['schema_version']

    assert {'asset_id', 'purchase_date', 'purchase_source', 'storage_location', 'notes', 'last_event_id', 'verified_at'} <= columns
    assert version == SCHEMA_VERSION
