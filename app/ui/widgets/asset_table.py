from PySide6.QtWidgets import QTableWidget

class AssetTable(QTableWidget):
    def refresh(self, assets):
        self.setRowCount(len(assets))
