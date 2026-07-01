from app.database.database import get_connection
from app.models.inventory_item import InventoryItem

class InventoryRepository:
    def add(self,item):
        with get_connection() as c:
            c.execute("INSERT INTO inventory(name,quantity,purchase_price) VALUES(?,?,?)",(item.name,item.quantity,item.purchase_price)); c.commit()
    def all(self):
        with get_connection() as c:
            return c.execute("SELECT id,name,quantity,purchase_price FROM inventory ORDER BY id DESC").fetchall()
    def get(self,id_):
        with get_connection() as c:
            return c.execute("SELECT id,name,quantity,purchase_price FROM inventory WHERE id=?",(id_,)).fetchone()
    def update(self,id_,item):
        with get_connection() as c:
            c.execute("UPDATE inventory SET name=?,quantity=?,purchase_price=? WHERE id=?",(item.name,item.quantity,item.purchase_price,id_)); c.commit()
    def delete(self,id_):
        with get_connection() as c:
            c.execute("DELETE FROM inventory WHERE id=?",(id_,)); c.commit()
