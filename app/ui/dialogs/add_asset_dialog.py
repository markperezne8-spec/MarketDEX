from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QLineEdit,QPushButton

class AddAssetDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Asset")
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel("Asset Name"))
        self.name=QLineEdit()
        layout.addWidget(self.name)
        layout.addWidget(QPushButton("Save"))
