from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)

from app.ui.widgets.asset_table import AssetTable
from app.ui.widgets.search_bar import SearchBar


class AssetManagerPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inventory")

        main_layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()

        self.add_button = QPushButton("+ Add Asset")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.refresh_button = QPushButton("Refresh")

        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_button)

        self.search = SearchBar()
        self.table = AssetTable()

        main_layout.addLayout(toolbar)
        main_layout.addWidget(self.search)
        main_layout.addWidget(self.table)

        self.refresh_button.clicked.connect(self.refresh_inventory)

    def refresh_inventory(self):
        print("Refreshing inventory...")
