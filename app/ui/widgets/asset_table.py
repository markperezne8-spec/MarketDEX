from PySide6.QtWidgets import QTableWidget

class AssetTable(QTableWidget):
    def __init__(self):
        super().__init__(0,8)
        self.setHorizontalHeaderLabels([
            "Name","Category","Set","Card #",
            "Condition","Qty","Cost","Value"
        ])
