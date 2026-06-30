ASSET_TABLE_SQL = '''
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
quantity INTEGER DEFAULT 1,
purchase_price REAL DEFAULT 0,
current_value REAL DEFAULT 0,
purchase_date TEXT,
purchase_source TEXT,
storage_location TEXT,
notes TEXT,
status TEXT DEFAULT 'inventory',
created_at TEXT,
updated_at TEXT
);
'''