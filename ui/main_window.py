from uuid import uuid4
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QDialog,QFormLayout,QLineEdit,QSpinBox,QDoubleSpinBox,QComboBox,QDialogButtonBox,QMessageBox
class AddAssetDialog(QDialog):
 def __init__(self,parent=None):
  super().__init__(parent); self.setWindowTitle('Add Asset Evidence'); f=QFormLayout(self); self.asset_id=QLineEdit(); self.name=QLineEdit(); self.asset_type=QLineEdit('SINGLE'); self.state=QComboBox(); self.state.addItems(['PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW']); self.qty=QSpinBox(); self.qty.setRange(0,1000000); self.cost=QDoubleSpinBox(); self.cost.setRange(0,999999999); self.cost.setDecimals(2)
  for label,w in [('Asset ID',self.asset_id),('Asset Name',self.name),('Asset Type',self.asset_type),('State',self.state),('Acquisition Quantity',self.qty),('Total Acquisition Cost',self.cost)]: f.addRow(label,w)
  b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); b.accepted.connect(self.accept); b.rejected.connect(self.reject); f.addRow(b)
 def evidence(self): return {'asset_id':self.asset_id.text().strip(),'asset_name':self.name.text().strip(),'asset_type':self.asset_type.text().strip(),'state':self.state.currentText(),'quantity':self.qty.value(),'total_cost_minor':round(self.cost.value()*100)}
class TransformDialog(QDialog):
 def __init__(self,sources,parent=None):
  super().__init__(parent); self.setWindowTitle('Transform Inventory Evidence'); f=QFormLayout(self); self.source=QComboBox(); [self.source.addItem(f"{r['asset_id']} — {r['asset_name']}",r['asset_id']) for r in sources]; self.qty=QSpinBox(); self.qty.setRange(1,1000000); self.result_id=QLineEdit(); self.result_name=QLineEdit(); self.result_type=QLineEdit('SINGLE'); self.result_qty=QSpinBox(); self.result_qty.setRange(1,1000000); self.cost=QDoubleSpinBox(); self.cost.setRange(0,999999999); self.cost.setDecimals(2)
  for label,w in [('Source Asset',self.source),('Source Quantity',self.qty),('Result Asset ID',self.result_id),('Result Asset Name',self.result_name),('Result Asset Type',self.result_type),('Result Quantity',self.result_qty),('Allocated Cost',self.cost)]: f.addRow(label,w)
  b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); b.accepted.connect(self.accept); b.rejected.connect(self.reject); f.addRow(b)
 def evidence(self): return {'source_asset_id':self.source.currentData(),'source_quantity':self.qty.value(),'asset_id':self.result_id.text().strip(),'asset_name':self.result_name.text().strip(),'asset_type':self.result_type.text().strip(),'quantity':self.result_qty.value(),'allocated_cost_minor':round(self.cost.value()*100)}
class MainWindow(QMainWindow):
 def __init__(self,database,services):
  super().__init__(); self.database,self.services=database,services; self.setWindowTitle('MarketDEX OS — M23.B1'); self.resize(1360,760); root=QWidget(); layout=QVBoxLayout(root); title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); layout.addWidget(title); layout.addWidget(QLabel('TRANSFORMATION + LINEAGE + COST CONSERVATION')); layout.addWidget(QLabel('Source → Transformation → Result • Controlled Write • Permanent Lineage • Conserved Cost'))
  bar=QHBoxLayout(); bar.addStretch(); add=QPushButton('Add Asset'); add.clicked.connect(self.add_asset); transform=QPushButton('Transform Inventory'); transform.clicked.connect(self.transform_inventory); bar.addWidget(add); bar.addWidget(transform); layout.addLayout(bar)
  self.table=QTableWidget(0,7); self.table.setHorizontalHeaderLabels(['Asset ID','Asset Name','Asset Type','State','Quantity','Total Cost','Lineage']); self.table.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.table); self.count=QLabel(); layout.addWidget(self.count); self.setCentralWidget(root); self.refresh()
 def rows(self):
  with self.database.connect() as c: return c.execute("SELECT a.asset_id,a.asset_name,a.asset_type,a.state,COALESCE(i.quantity,0) quantity,COALESCE(i.total_cost_minor,0) total_cost_minor,(SELECT source_asset_id FROM transformation_lineage l WHERE l.result_asset_id=a.asset_id LIMIT 1) source_id FROM assets a LEFT JOIN inventory_authority i ON i.asset_id=a.asset_id ORDER BY a.created_at,a.asset_id").fetchall()
 def refresh(self):
  rows=self.rows(); self.table.setRowCount(len(rows))
  for r,row in enumerate(rows):
   values=[row['asset_id'],row['asset_name'],row['asset_type'],row['state'],str(row['quantity']),f"${row['total_cost_minor']/100:,.2f}",f"FROM {row['source_id']}" if row['source_id'] else 'SOURCE']
   for col,value in enumerate(values): self.table.setItem(r,col,QTableWidgetItem(value))
  self.count.setText(f'Authoritative assets: {len(rows)}')
 def add_asset(self):
  d=AddAssetDialog(self)
  if d.exec()!=QDialog.DialogCode.Accepted:return
  e=d.evidence(); op=str(uuid4())
  try: self.services.asset.create_asset(request_id=f'{op}:asset',asset_id=e['asset_id'],asset_name=e['asset_name'],asset_type=e['asset_type'],state=e['state']); self.services.inventory.apply_acquisition(request_id=f'{op}:acquisition',asset_id=e['asset_id'],quantity=e['quantity'],total_cost_minor=e['total_cost_minor']); self.refresh(); QMessageBox.information(self,'Authoritative result verified','Asset and acquisition committed and verified.')
  except Exception as exc: self.refresh(); QMessageBox.critical(self,'Authoritative request blocked',str(exc))
 def transform_inventory(self):
  sources=[r for r in self.rows() if int(r['quantity'])>0]
  if not sources: QMessageBox.warning(self,'Transformation blocked','Zero available inventory is unsaleable and cannot be transformed.'); return
  d=TransformDialog(sources,self)
  if d.exec()!=QDialog.DialogCode.Accepted:return
  e=d.evidence(); op=str(uuid4())
  try: self.services.transformation.execute(request_id=f'{op}:transformation',transformation_id=f'TRF-{op}',source_asset_id=e['source_asset_id'],source_quantity=e['source_quantity'],outputs=[{'asset_id':e['asset_id'],'asset_name':e['asset_name'],'asset_type':e['asset_type'],'quantity':e['quantity'],'allocated_cost_minor':e['allocated_cost_minor']}]); self.refresh(); QMessageBox.information(self,'Transformation verified','Source consumption, result authority, lineage, and cost conservation verified.')
  except Exception as exc: self.refresh(); QMessageBox.critical(self,'Transformation blocked',str(exc))
