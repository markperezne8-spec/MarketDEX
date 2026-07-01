from PySide6.QtWidgets import QWidget,QVBoxLayout,QPushButton
from app.ui.dialogs.add_inventory_dialog import AddInventoryDialog

class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout(self)
        btn=QPushButton("➕ Add Inventory")
        btn.clicked.connect(self.add_item)
        layout.addWidget(btn)
    def add_item(self):
        AddInventoryDialog(self).exec()
