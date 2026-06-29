from PySide6.QtWidgets import QWidget,QVBoxLayout
from app.ui.widgets.asset_table import AssetTable
from app.ui.widgets.search_bar import SearchBar

class AssetManagerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout(self)
        layout.addWidget(SearchBar())
        layout.addWidget(AssetTable())
