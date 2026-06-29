import sqlite3
from app.database.schema import CREATE_ASSET_TABLE

class AssetService:
    def __init__(self, db_path="data/marketdex.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(CREATE_ASSET_TABLE)
        self.conn.commit()

    def add_asset(self, asset):
        self.conn.execute(
            "INSERT INTO assets(name,category,set_name,card_number,card_condition,quantity,purchase_price,current_value) VALUES(?,?,?,?,?,?,?,?)",
            (asset.name,asset.category,asset.set_name,asset.card_number,asset.condition,asset.quantity,asset.purchase_price,asset.current_value)
        )
        self.conn.commit()
