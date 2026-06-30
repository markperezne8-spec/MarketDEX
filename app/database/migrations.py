"""Database schema migrations.

Migrations are applied sequentially and idempotently.
Each migration should be safe to run multiple times.
"""

from app.database.schema import DATABASE_VERSION


def run_migrations(db_path):
    """
    Detect current database version and apply necessary migrations.
    
    Args:
        db_path: Path to the SQLite database file
    """
    from app.database.database_manager import DatabaseManager
    
    db = DatabaseManager(db_path)
    current_version = detect_database_version(db)
    target_version = DATABASE_VERSION
    
    if current_version < target_version:
        # Apply migrations sequentially
        for version in range(current_version + 1, target_version + 1):
            if version == 2:
                migrate_to_v2(db)
            elif version == 3:
                migrate_to_v3(db)
            elif version == 4:
                migrate_to_v4(db)


def detect_database_version(db):
    """
    Detect current database version by examining schema structure.
    
    Returns:
        int: Detected schema version (1, 2, 3, etc.)
    """
    try:
        with db.connect() as conn:
            # Get table info for assets table
            cursor = conn.execute("PRAGMA table_info(assets)")
            columns = {row[1] for row in cursor.fetchall()}  # row[1] is column name
            
            # v2+ has 'updated_at' column
            if 'updated_at' in columns:
                return 2
            
            # Default to v1 if table exists but lacks new columns
            return 1
    except Exception:
        # Table doesn't exist yet, return 0
        return 0


def migrate_to_v2(db):
    """
    Migrate from v1 to v2: Add new fields for extended asset tracking.
    
    New fields:
    - purchase_date: When the asset was purchased
    - purchase_source: Where the asset was purchased from
    - storage_location: Where the asset is physically stored
    - notes: Additional notes about the asset
    - status: Current status of the asset (default: 'inventory')
    - updated_at: Last update timestamp
    """
    with db.connect() as conn:
        # Add new columns if they don't exist (idempotent)
        # SQLite doesn't support "ADD COLUMN IF NOT EXISTS", so use error handling
        
        new_columns = [
            ('purchase_date', 'TEXT'),
            ('purchase_source', 'TEXT'),
            ('storage_location', 'TEXT'),
            ('notes', 'TEXT'),
            ('status', "TEXT DEFAULT 'inventory'"),
            ('updated_at', 'TEXT'),
        ]
        
        for col_name, col_type in new_columns:
            try:
                conn.execute(f"ALTER TABLE assets ADD COLUMN {col_name} {col_type}")
            except Exception:
                # Column already exists, continue
                pass
        
        conn.commit()


def migrate_to_v3(db):
    """
    Migrate from v2 to v3: Reserved for future schema changes.
    """
    # Stub for future implementation
    pass


def migrate_to_v4(db):
    """
    Migrate from v3 to v4: Reserved for future schema changes.
    """
    # Stub for future implementation
    pass
