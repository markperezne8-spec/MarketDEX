from PySide6.QtWidgets import QWidget, QVBoxLayout
from app.ui.widgets.inventory_toolbar import InventoryToolbar
from app.ui.widgets.search_bar import SearchBar

class AssetManagerPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.toolbar = InventoryToolbar()
        self.search = SearchBar()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.search)

        # TODO:
        # layout.addWidget(AssetTable())
        # Connect toolbar buttons to services in Commit 000003
