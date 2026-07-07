from uuid import uuid4
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QGridLayout,QGroupBox,QHBoxLayout,QTableWidget,QTableWidgetItem,QDialog,QFormLayout,QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox,QDialogButtonBox,QMessageBox


class AddAssetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add Inventory Asset')
        form = QFormLayout(self)
        self.name = QLineEdit()
        self.asset_type = QComboBox(); self.asset_type.addItems(['SINGLE','SEALED','SLAB','ACCESSORY'])
        self.quantity = QSpinBox(); self.quantity.setRange(0, 100000); self.quantity.setValue(1)
        self.cost = QDoubleSpinBox(); self.cost.setRange(0, 1000000); self.cost.setDecimals(2); self.cost.setPrefix('$')
        form.addRow('Asset Name', self.name); form.addRow('Asset Type', self.asset_type)
        form.addRow('Quantity', self.quantity); form.addRow('Total Cost', self.cost)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)


class MainWindow(QMainWindow):
    def __init__(self, service, inventory_service):
        super().__init__(); self.service=service; self.inventory_service=inventory_service
        self.setWindowTitle('MarketDEX OS — Mission Control'); self.resize(1480,860)
        root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); layout=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1)
        title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); layout.addWidget(title)
        subtitle=QLabel('MISSION CONTROL — LIVE SQLITE BUSINESS SNAPSHOT'); subtitle.setStyleSheet('font-size:15px;font-weight:600'); layout.addWidget(subtitle)
        self.values={}; grid=QGridLayout()
        cards=(('📦 Inventory Units','inventory_units'),('🗂️ Inventory Assets','inventory_asset_count'),('💰 Inventory Cost','inventory_cost_minor'),('🧾 Completed Sales','completed_sales'),('📈 Revenue','revenue_minor'),('💵 Profit','profit_minor'),('🛡️ Verified Audits','verified_audits'),('⚙️ Authority Events','authority_events'))
        for index,(label,key) in enumerate(cards):
            box=QGroupBox(label); box_layout=QVBoxLayout(box); value=QLabel('--'); value.setStyleSheet('font-size:24px;font-weight:700'); box_layout.addWidget(value); self.values[key]=value; grid.addWidget(box,index//2,index%2)
        layout.addLayout(grid)
        inventory_header=QHBoxLayout(); inventory_header.addWidget(QLabel('📦 INVENTORY')); inventory_header.addStretch(1)
        add_button=QPushButton('+ Add Asset'); add_button.clicked.connect(self.add_asset); inventory_header.addWidget(add_button); layout.addLayout(inventory_header)
        self.inventory_table=QTableWidget(0,4); self.inventory_table.setHorizontalHeaderLabels(['Asset','Type','Qty','Total Cost']); self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers); layout.addWidget(self.inventory_table)
        self.refresh_button=QPushButton('Refresh MarketDEX'); self.refresh_button.clicked.connect(self.refresh); layout.addWidget(self.refresh_button)
        self.footer=QLabel('Loading MarketDEX business authority...'); self.footer.setWordWrap(True); layout.addWidget(self.footer); self.setCentralWidget(root); self.refresh()

    @staticmethod
    def _money(minor): return f'${minor/100:,.2f}'

    def refresh(self):
        snapshot=self.service.snapshot()
        for key in ('inventory_units','inventory_asset_count','completed_sales','verified_audits','authority_events'): self.values[key].setText(f'{snapshot[key]:,}')
        for key in ('inventory_cost_minor','revenue_minor','profit_minor'): self.values[key].setText(self._money(snapshot[key]))
        rows=self.inventory_service.list_inventory(); self.inventory_table.setRowCount(len(rows))
        for row_index,row in enumerate(rows):
            for column,value in enumerate((row['asset_name'],row['asset_type'],row['quantity'],self._money(row['total_cost_minor']))): self.inventory_table.setItem(row_index,column,QTableWidgetItem(str(value)))
        self.inventory_table.resizeColumnsToContents(); self.footer.setText(f"LIVE DATABASE: {snapshot['database_path']} — refreshed from protected SQLite authority.")

    def add_asset(self):
        dialog=AddAssetDialog(self)
        if dialog.exec()!=QDialog.Accepted: return
        if not dialog.name.text().strip(): QMessageBox.warning(self,'Asset Required','Enter an asset name.'); return
        try:
            self.inventory_service.add_asset(asset_id=f'asset-{uuid4().hex}',asset_name=dialog.name.text(),asset_type=dialog.asset_type.currentText(),quantity=dialog.quantity.value(),total_cost_minor=round(dialog.cost.value()*100),request_id=f'ui-add-{uuid4().hex}')
            self.refresh()
        except Exception as exc: QMessageBox.critical(self,'Add Asset Failed',str(exc))
