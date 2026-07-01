from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QMessageBox
from app.ui.dialogs.add_inventory_dialog import AddInventoryDialog
from app.ui.dialogs.edit_inventory_dialog import EditInventoryDialog
from app.ui.widgets.inventory_table import InventoryTable
from app.repositories.inventory_repository import InventoryRepository

class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.repo=InventoryRepository(); self.table=InventoryTable()
        add=QPushButton("➕ Add"); edit=QPushButton("✏ Edit"); delete=QPushButton("🗑 Delete"); refresh=QPushButton("🔄 Refresh")
        add.clicked.connect(self.add_item); edit.clicked.connect(self.edit_item); delete.clicked.connect(self.delete_item); refresh.clicked.connect(self.table.refresh)
        top=QHBoxLayout(); [top.addWidget(b) for b in (add,edit,delete,refresh)]
        lay=QVBoxLayout(self); lay.addLayout(top); lay.addWidget(self.table)
    def add_item(self):
        if AddInventoryDialog(self).exec(): self.table.refresh()
    def edit_item(self):
        id_=self.table.selected_id()
        if id_ is None: QMessageBox.information(self,"Edit","Select a row."); return
        row=self.repo.get(id_)
        dlg=EditInventoryDialog(row,self)
        if dlg.exec():
            self.repo.update(id_,dlg.item()); self.table.refresh()
    def delete_item(self):
        id_=self.table.selected_id()
        if id_ is None: return
        if QMessageBox.question(self,"Confirm","Delete selected item?")==QMessageBox.Yes:
            self.repo.delete(id_); self.table.refresh()
