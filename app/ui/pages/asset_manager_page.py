from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QMessageBox
from app.ui.widgets.asset_table import AssetTable

class AssetManagerPage(QWidget):
    """Asset Manager page wired for future live database updates."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("Add Asset")
        self.refresh_btn = QPushButton("Refresh")

        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addStretch()

        self.table = AssetTable()

        layout.addLayout(toolbar)
        layout.addWidget(self.table)

        self.add_btn.clicked.connect(self.add_asset)
        self.refresh_btn.clicked.connect(self.refresh_assets)

    def add_asset(self):
        QMessageBox.information(
            self,
            "Alpha 2.4.2",
            "Add Asset dialog will be connected in Alpha 2.4.3."
        )

    def refresh_assets(self):
        self.table.setRowCount(0)
