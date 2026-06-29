ASSET_TABLE_SQL="""
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