from uuid import uuid4
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QDialog,QFormLayout,QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox,QDialogButtonBox,QMessageBox
class AddAssetDialog(QDialog):
 def __init__(self,parent=None):
  super().__init__(parent); self.setWindowTitle('Add Asset Evidence'); self.setMinimumWidth(420); form=QFormLayout(self)
  self.asset_id=QLineEdit(); self.name=QLineEdit(); self.asset_type=QLineEdit(); self.state=QComboBox(); self.state.addItems(['PLANNED','IN PROGRESS','COMPLETED','CANCELLED','REVIEW']); self.quantity=QSpinBox(); self.quantity.setRange(1,1000000); self.cost=QDoubleSpinBox(); self.cost.setRange(0,10000000); self.cost.setDecimals(2); self.cost.setPrefix('$')
  for label,w in [('Asset ID',self.asset_id),('Asset Name',self.name),('Asset Type',self.asset_type),('State',self.state),('Acquisition Quantity',self.quantity),('Total Acquisition Cost',self.cost)]: form.addRow(label,w)
  buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)
 def evidence(self): return {'asset_id':self.asset_id.text().strip(),'asset_name':self.name.text().strip(),'asset_type':self.asset_type.text().strip(),'state':self.state.currentText(),'quantity':self.quantity.value(),'total_cost_minor':round(self.cost.value()*100)}
class MainWindow(QMainWindow):
 def __init__(self,database,services):
  super().__init__(); self.database=database; self.services=services; self.setWindowTitle('MarketDEX OS — M22.B1'); self.resize(1100,650); root=QWidget(); layout=QVBoxLayout(root)
  title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size: 28px; font-weight: 700;'); status=QLabel('ASSET + INVENTORY OPERATING WORKFLOW'); status.setStyleSheet('font-size: 17px;'); authority=QLabel('Evidence • Validation • Explicit Request • Controlled Write • Persistent Authority')
  top=QHBoxLayout(); top.addWidget(title); top.addStretch(); self.add_button=QPushButton('Add Asset'); self.add_button.clicked.connect(self.add_asset); top.addWidget(self.add_button); layout.addLayout(top); layout.addWidget(status); layout.addWidget(authority)
  self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(['Asset ID','Asset Name','Asset Type','State','Quantity','Total Cost']); self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); layout.addWidget(self.table); self.count=QLabel(); layout.addWidget(self.count); self.setCentralWidget(root); self.refresh()
 def refresh(self):
  with self.database.connect() as c: rows=c.execute("SELECT a.asset_id,a.asset_name,a.asset_type,a.state,COALESCE(i.quantity,0) quantity,COALESCE(i.total_cost_minor,0) total_cost_minor FROM assets a LEFT JOIN inventory_authority i ON i.asset_id=a.asset_id ORDER BY a.created_at,a.asset_id").fetchall()
  self.table.setRowCount(len(rows))
  for r,row in enumerate(rows):
   values=[row['asset_id'],row['asset_name'],row['asset_type'],row['state'],str(row['quantity']),f"${row['total_cost_minor']/100:,.2f}"]
   for col,value in enumerate(values): self.table.setItem(r,col,QTableWidgetItem(value))
  self.count.setText(f'Authoritative assets: {len(rows)}')
 def add_asset(self):
  dialog=AddAssetDialog(self)
  if dialog.exec()!=QDialog.DialogCode.Accepted: return
  e=dialog.evidence()
  if not e['asset_id'] or not e['asset_name'] or not e['asset_type']: QMessageBox.warning(self,'Validation blocked','Asset ID, Asset Name, and Asset Type are required. No authoritative write occurred.'); return
  operation_id=str(uuid4())
  try:
   self.services.asset.create_asset(request_id=f'{operation_id}:asset',asset_id=e['asset_id'],asset_name=e['asset_name'],asset_type=e['asset_type'],state=e['state'])
   self.services.inventory.apply_acquisition(request_id=f'{operation_id}:acquisition',asset_id=e['asset_id'],quantity=e['quantity'],total_cost_minor=e['total_cost_minor']); self.refresh(); QMessageBox.information(self,'Authoritative result verified','Asset and acquisition committed, persisted, and post-write verified.')
  except Exception as exc: self.refresh(); QMessageBox.critical(self,'Authoritative request blocked',str(exc))
