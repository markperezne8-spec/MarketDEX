import sqlite3
from pathlib import Path

DB_PATH=Path("data/database/marketdex.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS inventory(
        id INTEGER PRIMARY KEY,
        name TEXT,
        quantity INTEGER,
        purchase_price REAL
    )""")
    return conn
