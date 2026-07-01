from PySide6.QtWidgets import QTableWidget,QTableWidgetItem
from app.repositories.inventory_repository import InventoryRepository

class InventoryTable(QTableWidget):
    def __init__(self):
        super().__init__(0,4)
        self.repo=InventoryRepository()
        self.setHorizontalHeaderLabels(["ID","Name","Qty","Price"])
        self.refresh()
    def refresh(self):
        rows=self.repo.all(); self.setRowCount(len(rows))
        for r,row in enumerate(rows):
            for c,v in enumerate(row):
                self.setItem(r,c,QTableWidgetItem(str(v)))
        self.resizeColumnsToContents()
    def selected_id(self):
        row=self.currentRow()
        return None if row<0 else int(self.item(row,0).text())
