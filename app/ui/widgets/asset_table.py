from PySide6.QtWidgets import QTableWidget,QTableWidgetItem

class AssetTable(QTableWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        headers=['Card Name','Set','Number','Qty','Purchase']
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def refresh(self,assets):
        self.setRowCount(len(assets))
        for r,asset in enumerate(assets):
            for c,val in enumerate(asset[:5]):
                self.setItem(r,c,QTableWidgetItem(str(val)))
