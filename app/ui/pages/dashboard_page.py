from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout(self)
        self.count=QLabel("Inventory: 0")
        layout.addWidget(self.count)
