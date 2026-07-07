from uuid import uuid4
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QGridLayout,QGroupBox,QHBoxLayout,QTableWidget,QTableWidgetItem,QDialog,QFormLayout,QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox,QDialogButtonBox,QMessageBox


class AddAssetDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle('Add Inventory Asset'); form=QFormLayout(self)
        self.name=QLineEdit(); self.asset_type=QComboBox(); self.asset_type.addItems(['SINGLE','SEALED','SLAB','ACCESSORY'])
        self.quantity=QSpinBox(); self.quantity.setRange(0,100000); self.quantity.setValue(1)
        self.cost=QDoubleSpinBox(); self.cost.setRange(0,1000000); self.cost.setDecimals(2); self.cost.setPrefix('$')
        form.addRow('Asset Name',self.name); form.addRow('Asset Type',self.asset_type); form.addRow('Quantity',self.quantity); form.addRow('Total Cost',self.cost)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)


class AdjustAssetDialog(QDialog):
    def __init__(self,detail,parent=None):
        super().__init__(parent); self.setWindowTitle('Adjust Inventory Asset'); form=QFormLayout(self)
        form.addRow('Asset',QLabel(detail['asset_name'])); form.addRow('Current Quantity',QLabel(str(detail['quantity']))); form.addRow('Current Cost',QLabel(f"${detail['total_cost_minor']/100:,.2f}"))
        self.quantity_delta=QSpinBox(); self.quantity_delta.setRange(-100000,100000); self.quantity_delta.setPrefix('Delta ')
        self.cost_delta=QDoubleSpinBox(); self.cost_delta.setRange(-1000000,1000000); self.cost_delta.setDecimals(2); self.cost_delta.setPrefix('Delta $')
        form.addRow('Quantity Adjustment',self.quantity_delta); form.addRow('Cost Adjustment',self.cost_delta)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)


class MainWindow(QMainWindow):
    def __init__(self,service,inventory_service):
        super().__init__(); self.service=service; self.inventory_service=inventory_service; self.inventory_rows=[]
        self.setWindowTitle('MarketDEX OS — Mission Control'); self.resize(1480,860)
        root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); layout=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1)
        title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); layout.addWidget(title)
        subtitle=QLabel('MISSION CONTROL — LIVE SQLITE BUSINESS SNAPSHOT'); subtitle.setStyleSheet('font-size:15px;font-weight:600'); layout.addWidget(subtitle)
        self.values={}; grid=QGridLayout(); cards=(('📦 Inventory Units','inventory_units'),('🗂️ Inventory Assets','inventory_asset_count'),('💰 Inventory Cost','inventory_cost_minor'),('🧾 Completed Sales','completed_sales'),('📈 Revenue','revenue_minor'),('💵 Profit','profit_minor'),('🛡️ Verified Audits','verified_audits'),('⚙️ Authority Events','authority_events'))
        for index,(label,key) in enumerate(cards):
            box=QGroupBox(label); box_layout=QVBoxLayout(box); value=QLabel('--'); value.setStyleSheet('font-size:24px;font-weight:700'); box_layout.addWidget(value); self.values[key]=value; grid.addWidget(box,index//2,index%2)
        layout.addLayout(grid)
        inventory_header=QHBoxLayout(); inventory_header.addWidget(QLabel('📦 INVENTORY')); inventory_header.addStretch(1)
        self.adjust_button=QPushButton('Adjust Selected'); self.adjust_button.setEnabled(False); self.adjust_button.clicked.connect(self.adjust_selected); inventory_header.addWidget(self.adjust_button)
        add_button=QPushButton('+ Add Asset'); add_button.clicked.connect(self.add_asset); inventory_header.addWidget(add_button); layout.addLayout(inventory_header)
        filter_bar=QHBoxLayout(); self.inventory_search=QLineEdit(); self.inventory_search.setPlaceholderText('Search inventory by asset name...'); self.inventory_search.textChanged.connect(self.refresh_inventory); filter_bar.addWidget(self.inventory_search)
        self.inventory_type_filter=QComboBox(); self.inventory_type_filter.addItems(['ALL','SINGLE','SEALED','SLAB','ACCESSORY']); self.inventory_type_filter.currentTextChanged.connect(self.refresh_inventory); filter_bar.addWidget(self.inventory_type_filter); layout.addLayout(filter_bar)
        sort_bar=QHBoxLayout(); sort_bar.addWidget(QLabel('Sort by'))
        self.inventory_sort=QComboBox(); self.inventory_sort.addItems(['NAME','TYPE','QUANTITY','TOTAL COST']); self.inventory_sort.currentTextChanged.connect(self.refresh_inventory); sort_bar.addWidget(self.inventory_sort)
        self.inventory_sort_order=QComboBox(); self.inventory_sort_order.addItems(['ASC','DESC']); self.inventory_sort_order.currentTextChanged.connect(self.refresh_inventory); sort_bar.addWidget(self.inventory_sort_order); sort_bar.addStretch(1); layout.addLayout(sort_bar)
        summary_bar=QHBoxLayout(); self.inventory_summary={}
        for label,key in (('Assets','asset_count'),('Units','total_units'),('Filtered Cost','total_cost_minor')):
            box=QGroupBox(label); box_layout=QVBoxLayout(box); value=QLabel('--'); value.setStyleSheet('font-size:18px;font-weight:700'); box_layout.addWidget(value); self.inventory_summary[key]=value; summary_bar.addWidget(box)
        layout.addLayout(summary_bar)
        self.inventory_table=QTableWidget(0,4); self.inventory_table.setHorizontalHeaderLabels(['Asset','Type','Qty','Total Cost']); self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers); self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows); self.inventory_table.itemSelectionChanged.connect(self.show_selected); layout.addWidget(self.inventory_table)
        self.inventory_result=QLabel(''); layout.addWidget(self.inventory_result)
        self.asset_detail=QLabel('Select an inventory asset to view details.'); self.asset_detail.setWordWrap(True); layout.addWidget(self.asset_detail)
        self.refresh_button=QPushButton('Refresh MarketDEX'); self.refresh_button.clicked.connect(self.refresh); layout.addWidget(self.refresh_button)
        self.footer=QLabel('Loading MarketDEX business authority...'); self.footer.setWordWrap(True); layout.addWidget(self.footer); self.setCentralWidget(root); self.refresh()

    @staticmethod
    def _money(minor): return f'${minor/100:,.2f}'

    def refresh_inventory(self):
        self.inventory_rows=self.inventory_service.list_inventory(search_text=self.inventory_search.text(),asset_type=self.inventory_type_filter.currentText(),sort_key=self.inventory_sort.currentText(),sort_order=self.inventory_sort_order.currentText()); self.inventory_table.setRowCount(len(self.inventory_rows))
        summary=self.inventory_service.summarize_inventory(self.inventory_rows); self.inventory_summary['asset_count'].setText(f"{summary['asset_count']:,}"); self.inventory_summary['total_units'].setText(f"{summary['total_units']:,}"); self.inventory_summary['total_cost_minor'].setText(self._money(summary['total_cost_minor']))
        for row_index,row in enumerate(self.inventory_rows):
            for column,value in enumerate((row['asset_name'],row['asset_type'],row['quantity'],self._money(row['total_cost_minor']))): self.inventory_table.setItem(row_index,column,QTableWidgetItem(str(value)))
        self.inventory_table.resizeColumnsToContents(); self.inventory_result.setText(f"Showing {len(self.inventory_rows):,} matching inventory asset(s) • {self.inventory_sort.currentText()} {self.inventory_sort_order.currentText()}"); self.show_selected()

    def refresh(self):
        snapshot=self.service.snapshot()
        for key in ('inventory_units','inventory_asset_count','completed_sales','verified_audits','authority_events'): self.values[key].setText(f'{snapshot[key]:,}')
        for key in ('inventory_cost_minor','revenue_minor','profit_minor'): self.values[key].setText(self._money(snapshot[key]))
        self.refresh_inventory(); self.footer.setText(f"LIVE DATABASE: {snapshot['database_path']} — refreshed from protected SQLite authority.")

    def selected_asset_id(self):
        row=self.inventory_table.currentRow(); return self.inventory_rows[row]['asset_id'] if 0<=row<len(self.inventory_rows) else None

    def show_selected(self):
        asset_id=self.selected_asset_id(); self.adjust_button.setEnabled(asset_id is not None)
        if asset_id is None: self.asset_detail.setText('Select an inventory asset to view details.'); return
        detail=self.inventory_service.get_asset_detail(asset_id)
        self.asset_detail.setText(f"SELECTED: {detail['asset_name']}  •  {detail['asset_type']}  •  Qty {detail['quantity']}  •  Cost {self._money(detail['total_cost_minor'])}  •  {detail['state']}")

    def add_asset(self):
        dialog=AddAssetDialog(self)
        if dialog.exec()!=QDialog.Accepted:return
        if not dialog.name.text().strip(): QMessageBox.warning(self,'Asset Required','Enter an asset name.'); return
        try:self.inventory_service.add_asset(asset_id=f'asset-{uuid4().hex}',asset_name=dialog.name.text(),asset_type=dialog.asset_type.currentText(),quantity=dialog.quantity.value(),total_cost_minor=round(dialog.cost.value()*100),request_id=f'ui-add-{uuid4().hex}'); self.refresh()
        except Exception as exc:QMessageBox.critical(self,'Add Asset Failed',str(exc))

    def adjust_selected(self):
        asset_id=self.selected_asset_id()
        if asset_id is None:return
        dialog=AdjustAssetDialog(self.inventory_service.get_asset_detail(asset_id),self)
        if dialog.exec()!=QDialog.Accepted:return
        try:self.inventory_service.adjust_asset(asset_id=asset_id,quantity_delta=dialog.quantity_delta.value(),cost_delta_minor=round(dialog.cost_delta.value()*100),request_id=f'ui-adjust-{uuid4().hex}'); self.refresh()
        except Exception as exc:QMessageBox.critical(self,'Adjustment Blocked',str(exc))