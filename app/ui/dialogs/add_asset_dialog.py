from PySide6.QtWidgets import QDialog,QFormLayout,QLineEdit,QSpinBox,QDoubleSpinBox,QDialogButtonBox

class AddAssetDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Asset")
        layout=QFormLayout(self)
        layout.addRow("Name",QLineEdit())
        layout.addRow("Category",QLineEdit())
        layout.addRow("Quantity",QSpinBox())
        price=QDoubleSpinBox(); price.setMaximum(1_000_000)
        layout.addRow("Purchase Price",price)
        layout.addWidget(QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel))
