from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QLineEdit,QDoubleSpinBox,QSpinBox,QDialogButtonBox

class AddAssetDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Asset")
        layout=QVBoxLayout(self)
        form=QFormLayout()
        self.name=QLineEdit()
        self.set_name=QLineEdit()
        self.card_number=QLineEdit()
        self.purchase=QDoubleSpinBox(); self.purchase.setMaximum(1000000); self.purchase.setPrefix("$")
        self.quantity=QSpinBox(); self.quantity.setMinimum(1)
        form.addRow("Card Name",self.name)
        form.addRow("Set",self.set_name)
        form.addRow("Card Number",self.card_number)
        form.addRow("Purchase Price",self.purchase)
        form.addRow("Quantity",self.quantity)
        layout.addLayout(form)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
