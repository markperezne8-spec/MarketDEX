"""
MarketDEX Database Manager
Alpha 2.4
"""

from pathlib import Path
import sqlite3


class DatabaseManager:
    """Single point of access for the MarketDEX SQLite database."""

    def __init__(self, db_path: str = "data/marketdex.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: sqlite3.Connection | None = None

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def execute(self, sql: str, params: tuple = ()):
        conn = self.connect()
        cur = conn.execute(sql, params)
        conn.commit()
        return cur

    def query(self, sql: str, params: tuple = ()):
        return self.execute(sql, params).fetchall()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
