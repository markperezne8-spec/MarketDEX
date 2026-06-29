from app.database.database_manager import DatabaseManager
from app.models.asset import Asset

class AssetRepository:
    """Handles Asset persistence."""

    def __init__(self, db=None):
        self.db=db or DatabaseManager()

    def initialize(self):
        self.db.execute("""
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
        )
        """)

    def add(self, asset: Asset):
        self.db.execute(
            """INSERT INTO assets
            (name,category,set_name,card_number,card_condition,quantity,purchase_price,current_value)
            VALUES(?,?,?,?,?,?,?,?)""",
            (asset.name,asset.category,asset.set_name,asset.card_number,
             asset.condition,asset.quantity,asset.purchase_price,asset.current_value)
        )

    def all(self):
        return self.db.query("SELECT * FROM assets ORDER BY name")
