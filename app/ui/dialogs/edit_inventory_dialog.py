from PySide6.QtWidgets import QDialog,QFormLayout,QLineEdit,QSpinBox,QDoubleSpinBox,QVBoxLayout,QPushButton
from app.models.inventory_item import InventoryItem

class EditInventoryDialog(QDialog):
    def __init__(self,row,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Inventory")
        self.name=QLineEdit(str(row[1]))
        self.qty=QSpinBox(); self.qty.setMaximum(1000000); self.qty.setValue(int(row[2]))
        self.price=QDoubleSpinBox(); self.price.setMaximum(1_000_000); self.price.setDecimals(2); self.price.setValue(float(row[3]))
        form=QFormLayout()
        form.addRow("Name",self.name)
        form.addRow("Quantity",self.qty)
        form.addRow("Purchase Price",self.price)
        btn=QPushButton("Save")
        btn.clicked.connect(self.accept)
        lay=QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(btn)
    def item(self):
        return InventoryItem(self.name.text(),self.qty.value(),self.price.value())
