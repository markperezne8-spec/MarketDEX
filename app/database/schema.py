CREATE_ASSET_TABLE = """
CREATE TABLE IF NOT EXISTS assets(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT,
 category TEXT,
 set_name TEXT,
 card_number TEXT,
 card_condition TEXT,
 quantity INTEGER,
 purchase_price REAL,
 current_value REAL
);
"""
