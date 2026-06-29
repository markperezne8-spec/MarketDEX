from PySide6.QtWidgets import (
    QDialog,QFormLayout,QLineEdit,QSpinBox,QDoubleSpinBox,
    QDialogButtonBox
)

class AddAssetDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Asset")
        layout=QFormLayout(self)

        self.name=QLineEdit()
        self.category=QLineEdit()
        self.set_name=QLineEdit()
        self.card_number=QLineEdit()
        self.qty=QSpinBox(); self.qty.setMinimum(1)
        self.cost=QDoubleSpinBox(); self.cost.setMaximum(1_000_000)
        self.value=QDoubleSpinBox(); self.value.setMaximum(1_000_000)

        layout.addRow("Name",self.name)
        layout.addRow("Category",self.category)
        layout.addRow("Set",self.set_name)
        layout.addRow("Card #",self.card_number)
        layout.addRow("Quantity",self.qty)
        layout.addRow("Purchase Price",self.cost)
        layout.addRow("Current Value",self.value)

        buttons=QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save|
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
