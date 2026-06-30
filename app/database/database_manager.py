from pathlib import Path
import sqlite3
from app.database.schema import ASSET_TABLE_SQL


class DatabaseManager:
    """Manages SQLite database connections and schema initialization."""
    
    def __init__(self, db_path="data/marketdex.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        """Create and return a database connection with Row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        """Initialize database schema and run migrations."""
        # Create initial table (idempotent)
        with self.connect() as conn:
            conn.execute(ASSET_TABLE_SQL)
            conn.commit()
        
        # Run migrations to upgrade schema if needed
        from app.database.migrations import run_migrations
        run_migrations(str(self.db_path))
