from uuid import uuid4
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QDialog,QFormLayout,QSpinBox,QDoubleSpinBox,QComboBox,QDialogButtonBox,QMessageBox
from ui.main_window_m23 import AddAssetDialog, TransformDialog

class SaleDialog(QDialog):
    def __init__(self,sources,parent=None):
        super().__init__(parent); self.setWindowTitle('Record Sale Evidence')
        f=QFormLayout(self); self.asset=QComboBox()
        [self.asset.addItem(f"{r['asset_id']} — {r['asset_name']} — Qty {r['quantity']}",r['asset_id']) for r in sources]
        self.qty=QSpinBox(); self.qty.setRange(1,1000000)
        self.revenue=QDoubleSpinBox(); self.fees=QDoubleSpinBox(); self.shipping=QDoubleSpinBox(); self.packaging=QDoubleSpinBox()
        for x in (self.revenue,self.fees,self.shipping,self.packaging): x.setRange(0,999999999); x.setDecimals(2)
        for label,wid in [('Asset',self.asset),('Sale Quantity',self.qty),('Sale Revenue',self.revenue),('Marketplace Fees',self.fees),('Shipping Cost',self.shipping),('Packaging Cost',self.packaging)]: f.addRow(label,wid)
        b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); b.accepted.connect(self.accept); b.rejected.connect(self.reject); f.addRow(b)
    def evidence(self):
        return {'asset_id':self.asset.currentData(),'quantity':self.qty.value(),'revenue_minor':round(self.revenue.value()*100),'marketplace_fees_minor':round(self.fees.value()*100),'shipping_minor':round(self.shipping.value()*100),'packaging_minor':round(self.packaging.value()*100)}

class MainWindow(QMainWindow):
    def __init__(self,database,services):
        super().__init__(); self.database,self.services=database,services
        self.setWindowTitle('MarketDEX OS — M24.B1'); self.resize(1380,760)
        root=QWidget(); layout=QVBoxLayout(root)
        title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); layout.addWidget(title)
        layout.addWidget(QLabel('SALES + PROFIT AUTHORITY'))
        layout.addWidget(QLabel('Revenue → Fees → Shipping + Packaging → COGS → Net Profit • Controlled Sale • Verified Financial Truth'))
        bar=QHBoxLayout(); bar.addStretch()
        add=QPushButton('Add Asset'); add.clicked.connect(self.add_asset)
        transform=QPushButton('Transform Inventory'); transform.clicked.connect(self.transform_inventory)
        sale=QPushButton('Record Sale'); sale.clicked.connect(self.record_sale)
        bar.addWidget(add); bar.addWidget(transform); bar.addWidget(sale); layout.addLayout(bar)
        self.table=QTableWidget(0,9); self.table.setHorizontalHeaderLabels(['Asset ID','Asset Name','State','Quantity','Total Cost','Revenue','COGS','Profit','Lineage'])
        self.table.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.table)
        self.count=QLabel(); layout.addWidget(self.count); self.setCentralWidget(root); self.refresh()

    def rows(self):
        with self.database.connect() as c:
            return c.execute("""SELECT a.asset_id,a.asset_name,a.state,COALESCE(i.quantity,0) quantity,COALESCE(i.total_cost_minor,0) total_cost_minor,
            COALESCE((SELECT SUM(revenue_minor) FROM sales s WHERE s.asset_id=a.asset_id),0) revenue_minor,
            COALESCE((SELECT SUM(cogs_minor) FROM sales s WHERE s.asset_id=a.asset_id),0) cogs_minor,
            COALESCE((SELECT SUM(profit_minor) FROM sales s WHERE s.asset_id=a.asset_id),0) profit_minor,
            (SELECT source_asset_id FROM transformation_lineage l WHERE l.result_asset_id=a.asset_id LIMIT 1) source_id
            FROM assets a LEFT JOIN inventory_authority i ON i.asset_id=a.asset_id ORDER BY a.created_at,a.asset_id""").fetchall()

    def refresh(self):
        rows=self.rows(); self.table.setRowCount(len(rows))
        for r,row in enumerate(rows):
            vals=[row['asset_id'],row['asset_name'],row['state'],str(row['quantity']),f"${row['total_cost_minor']/100:,.2f}",f"${row['revenue_minor']/100:,.2f}",f"${row['cogs_minor']/100:,.2f}",f"${row['profit_minor']/100:,.2f}",f"FROM {row['source_id']}" if row['source_id'] else 'SOURCE']
            for col,v in enumerate(vals): self.table.setItem(r,col,QTableWidgetItem(v))
        self.count.setText(f'Authoritative assets: {len(rows)}')

    def add_asset(self):
        d=AddAssetDialog(self)
        if d.exec()!=QDialog.DialogCode.Accepted:return
        e=d.evidence(); op=str(uuid4())
        try:
            self.services.asset.create_asset(request_id=f'{op}:asset',asset_id=e['asset_id'],asset_name=e['asset_name'],asset_type=e['asset_type'],state=e['state'])
            self.services.inventory.apply_acquisition(request_id=f'{op}:acquisition',asset_id=e['asset_id'],quantity=e['quantity'],total_cost_minor=e['total_cost_minor'])
            self.refresh(); QMessageBox.information(self,'Authoritative result verified','Asset and acquisition committed and verified.')
        except Exception as exc: self.refresh(); QMessageBox.critical(self,'Authoritative request blocked',str(exc))

    def transform_inventory(self):
        sources=[r for r in self.rows() if int(r['quantity'])>0]
        if not sources: QMessageBox.warning(self,'Transformation blocked','Zero available inventory is unsaleable and cannot be transformed.'); return
        d=TransformDialog(sources,self)
        if d.exec()!=QDialog.DialogCode.Accepted:return
        e=d.evidence(); op=str(uuid4())
        try:
            self.services.transformation.execute(request_id=f'{op}:transformation',transformation_id=f'TRF-{op}',source_asset_id=e['source_asset_id'],source_quantity=e['source_quantity'],outputs=[{'asset_id':e['asset_id'],'asset_name':e['asset_name'],'asset_type':e['asset_type'],'quantity':e['quantity'],'allocated_cost_minor':e['allocated_cost_minor']}])
            self.refresh(); QMessageBox.information(self,'Transformation verified','Source consumption, result authority, lineage, and cost conservation verified.')
        except Exception as exc: self.refresh(); QMessageBox.critical(self,'Transformation blocked',str(exc))

    def record_sale(self):
        sources=[r for r in self.rows() if int(r['quantity'])>0]
        if not sources: QMessageBox.warning(self,'Sale blocked','Zero available inventory is unsaleable.'); return
        d=SaleDialog(sources,self)
        if d.exec()!=QDialog.DialogCode.Accepted:return
        e=d.evidence(); op=str(uuid4())
        try:
            self.services.sales.record_sale(request_id=f'{op}:sale',sale_id=f'SALE-{op}',**e)
            self.refresh(); QMessageBox.information(self,'Sale verified','Inventory decrement, COGS, and net profit financial truth verified.')
        except Exception as exc: self.refresh(); QMessageBox.critical(self,'Sale blocked',str(exc))
