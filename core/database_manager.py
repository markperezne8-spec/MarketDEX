from __future__ import annotations
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone
from .schema import SCHEMA_SQL, SCHEMA_VERSION

class DatabaseManager:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys = ON')
        connection.execute('PRAGMA journal_mode = WAL')
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA_SQL)
            row = connection.execute('SELECT schema_version FROM schema_metadata ORDER BY rowid DESC LIMIT 1').fetchone()
            if row is None:
                connection.execute('INSERT INTO schema_metadata(schema_version, applied_at) VALUES (?, ?)',
                                   (SCHEMA_VERSION, datetime.now(timezone.utc).isoformat()))
            elif row['schema_version'] != SCHEMA_VERSION:
                raise RuntimeError(f'Unsupported schema version: {row["schema_version"]}')

    @contextmanager
    def transaction(self):
        connection = self.connect()
        try:
            connection.execute('BEGIN IMMEDIATE')
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
