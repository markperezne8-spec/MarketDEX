from __future__ import annotations

from pathlib import Path

from database.database_manager import DatabaseManager


def test_initialize_creates_schema_version(tmp_path: Path) -> None:
    database_path = tmp_path / "marketdex-test.db"
    manager = DatabaseManager(database_path)

    manager.initialize()

    with manager.connect() as connection:
        row = connection.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        ).fetchone()

    assert row is not None
    assert row["version"] == 1
