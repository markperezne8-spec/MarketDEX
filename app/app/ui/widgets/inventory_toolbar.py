from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class InventoryToolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.add_button = QPushButton("+ Add Asset")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        layout.addWidget(self.add_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.refresh_button)
        layout.addStretch()
