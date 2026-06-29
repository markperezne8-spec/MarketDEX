from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton
from app.ui.widgets.asset_table import AssetTable

class AssetManagerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout(self)
        bar=QHBoxLayout()
        for text in ("Add Asset","Edit","Delete","Refresh"):
            bar.addWidget(QPushButton(text))
        layout.addLayout(bar)
        layout.addWidget(AssetTable())
