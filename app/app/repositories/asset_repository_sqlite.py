import sqlite3

class AssetRepositorySQLite:
    def __init__(self, db_path="data/marketdex.db"):
        self.db_path=db_path

    def add(self, asset):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO assets(name,set_name,card_number,purchase_price,quantity) VALUES(?,?,?,?,?)",
                (asset.name, asset.set_name, asset.card_number, asset.purchase_price, asset.quantity)
            )
            conn.commit()
