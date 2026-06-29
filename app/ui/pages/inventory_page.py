from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel
class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(self)
        l.addWidget(QLabel("Inventory"))
