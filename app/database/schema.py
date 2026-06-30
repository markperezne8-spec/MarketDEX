# Database schema versioning
DATABASE_VERSION = 1

# Schema v1 (Original)
ASSET_TABLE_V1 = """
CREATE TABLE IF NOT EXISTS assets(
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE,
    name TEXT NOT NULL,
    asset_type TEXT,
    set_name TEXT,
    card_number TEXT,
    rarity TEXT,
    variant TEXT,
    card_condition TEXT,
    quantity INTEGER,
    purchase_price REAL,
    current_value REAL,
    created_at TEXT
);
"""

# Schema v2 (Build 002.1 - Extended fields)
ASSET_TABLE_V2 = """
CREATE TABLE IF NOT EXISTS assets(
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE,
    name TEXT NOT NULL,
    asset_type TEXT,
    set_name TEXT,
    card_number TEXT,
    rarity TEXT,
    variant TEXT,
    card_condition TEXT,
    quantity INTEGER,
    purchase_price REAL,
    current_value REAL,
    purchase_date TEXT,
    purchase_source TEXT,
    storage_location TEXT,
    notes TEXT,
    status TEXT DEFAULT 'inventory',
    created_at TEXT,
    updated_at TEXT
);
"""

# Current schema (used for new databases)
ASSET_TABLE_SQL = ASSET_TABLE_V2