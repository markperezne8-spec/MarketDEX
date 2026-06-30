from pathlib import Path
import sqlite3
from app.database.schema import ASSET_TABLE_SQL

class DatabaseManager:
    def __init__(self, db_path="data/marketdex.db"):
        self.db_path=Path(db_path)
        self.db_path.parent.mkdir(parents=True,exist_ok=True)

    def connect(self):
        conn=sqlite3.connect(self.db_path)
        conn.row_factory=sqlite3.Row
        return conn

    def initialize(self):
        with self.connect() as conn:
            conn.execute(ASSET_TABLE_SQL)
            conn.commit()
