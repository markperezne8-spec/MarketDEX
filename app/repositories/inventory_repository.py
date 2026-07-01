from app.database.database import get_connection
from app.models.inventory_item import InventoryItem

class InventoryRepository:
    def add(self,item:InventoryItem):
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO inventory(name,quantity,purchase_price) VALUES(?,?,?)",
                (item.name,item.quantity,item.purchase_price)
            )
            conn.commit()

    def all(self):
        with get_connection() as conn:
            return conn.execute(
                "SELECT id,name,quantity,purchase_price FROM inventory ORDER BY id DESC"
            ).fetchall()

    def count(self):
        with get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]

    def total_investment(self):
        with get_connection() as conn:
            return float(conn.execute(
                "SELECT COALESCE(SUM(quantity*purchase_price),0) FROM inventory"
            ).fetchone()[0] or 0)
