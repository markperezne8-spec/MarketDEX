from PySide6.QtWidgets import QDialog,QFormLayout,QLineEdit,QSpinBox,QDoubleSpinBox,QPushButton,QVBoxLayout
from app.models.inventory_item import InventoryItem
from app.services.inventory_service import InventoryService

class AddInventoryDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Inventory")
        self.service=InventoryService()
        self.name=QLineEdit()
        self.qty=QSpinBox(); self.qty.setMaximum(1000000)
        self.price=QDoubleSpinBox(); self.price.setMaximum(1_000_000); self.price.setDecimals(2)
        form=QFormLayout()
        form.addRow("Name",self.name)
        form.addRow("Quantity",self.qty)
        form.addRow("Purchase Price",self.price)
        btn=QPushButton("Save")
        btn.clicked.connect(self.save)
        layout=QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(btn)
    def save(self):
        item=InventoryItem(
            name=self.name.text(),
            quantity=self.qty.value(),
            purchase_price=self.price.value()
        )
        self.service.add_item(item)
        self.accept()
