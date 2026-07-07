from uuid import uuid4
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QDialog,QFormLayout,QSpinBox,QDoubleSpinBox,QComboBox,QLineEdit,QDialogButtonBox,QMessageBox
from ui.main_window_m24 import AddAssetDialog,TransformDialog,SaleDialog

class ReturnDialog(QDialog):
 def __init__(self,sales,parent=None):
  super().__init__(parent); self.setWindowTitle('Authorized Return Evidence'); f=QFormLayout(self)
  self.sale=QComboBox(); [self.sale.addItem(f"{r['sale_id']} — {r['asset_id']} — Qty {r['quantity']}",r['sale_id']) for r in sales]
  self.qty=QSpinBox(); self.qty.setRange(1,1000000); self.condition=QLineEdit(); self.restock=QComboBox(); self.restock.addItem('VALIDATED RESTOCK','YES'); self.restock.addItem('NO RESTOCK','NO')
  self.refund=QDoubleSpinBox(); self.refund.setRange(0,999999999); self.refund.setDecimals(2)
  for label,w in [('Original Completed Sale',self.sale),('Return Quantity',self.qty),('Condition Evidence',self.condition),('Return-to-Inventory Decision',self.restock),('Authorized Refund',self.refund)]: f.addRow(label,w)
  b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); b.accepted.connect(self.accept); b.rejected.connect(self.reject); f.addRow(b)
 def evidence(self): return {'sale_id':self.sale.currentData(),'quantity':self.qty.value(),'condition_evidence':self.condition.text().strip(),'restock_authorized':self.restock.currentData()=='YES','refund_minor':round(self.refund.value()*100)}

class MainWindow(QMainWindow):
 def __init__(self,database,services):
  super().__init__(); self.database,self.services=database,services; self.setWindowTitle('MarketDEX OS — M25.B1'); self.resize(1380,760)
  root=QWidget(); layout=QVBoxLayout(root); title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); layout.addWidget(title)
  layout.addWidget(QLabel('RETURNS + CORRECTIONS + REVERSALS AUTHORITY')); layout.addWidget(QLabel('Original Authority Immutable • Append-Only Corrective Lineage • Derived Inventory + Financial Effects • Replay Defense'))
  bar=QHBoxLayout(); bar.addStretch(); ret=QPushButton('Authorized Return'); ret.clicked.connect(self.authorized_return); cor=QPushButton('Create Correction'); cor.clicked.connect(self.correction); rev=QPushButton('Create Reversal'); rev.clicked.connect(self.reversal); bar.addWidget(ret); bar.addWidget(cor); bar.addWidget(rev); layout.addLayout(bar)
  self.table=QTableWidget(0,8); self.table.setHorizontalHeaderLabels(['Authority','ID','Original Event','Asset / Sale','Inventory Effect','Financial Effect','Profit Effect','Status']); self.table.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.table)
  self.status=QLabel(); layout.addWidget(self.status); self.setCentralWidget(root); self.refresh()
 def refresh(self):
  with self.database.connect() as c:
   rows=[]
   for r in c.execute("""SELECT 'RETURN' authority,return_id id,(SELECT original_event_id FROM return_events re WHERE re.return_id=returns.return_id) original_event,asset_id||' / '||sale_id subject,restored_cost_minor,refund_minor,profit_restatement_minor FROM returns ORDER BY created_at"""): rows.append((r['authority'],r['id'],r['original_event'],r['subject'],f"+${r['restored_cost_minor']/100:.2f} cost",f"-${r['refund_minor']/100:.2f}",f"${r['profit_restatement_minor']/100:.2f}",'VERIFIED'))
   for r in c.execute("SELECT 'CORRECTION' authority,correction_event_id id,original_event_id FROM correction_events ORDER BY recorded_at"): rows.append((r['authority'],r['id'],r['original_event_id'],'TARGET EVENT','$0.00','$0.00','$0.00','VERIFIED'))
   for r in c.execute("SELECT 'REVERSAL' authority,reversal_event_id id,original_event_id FROM reversal_events ORDER BY recorded_at"): rows.append((r['authority'],r['id'],r['original_event_id'],'ORIGINAL EVENT','$0.00','$0.00','$0.00','VERIFIED'))
   self.table.setRowCount(len(rows))
   for i,row in enumerate(rows):
    for j,v in enumerate(row): self.table.setItem(i,j,QTableWidgetItem(str(v)))
   self.status.setText(f'Append-only M25 authority results: {len(rows)}')
 def sales(self):
  with self.database.connect() as c: return c.execute("SELECT sale_id,asset_id,quantity,created_event_id FROM sales WHERE state='COMPLETED' ORDER BY created_at").fetchall()
 def authorized_return(self):
  sales=self.sales()
  if not sales: QMessageBox.warning(self,'Return blocked','No matched completed original sale.'); return
  d=ReturnDialog(sales,self)
  if d.exec()!=QDialog.DialogCode.Accepted:return
  e=d.evidence(); op=str(uuid4())
  try: self.services.return_service.execute(request_id=f'{op}:return',return_id=f'RET-{op}',**e); self.refresh(); QMessageBox.information(self,'Authoritative return verified','Original sale immutable. Return lineage, inventory restoration, cost restoration, refund impact, and profit restatement verified.')
  except Exception as exc: self.refresh(); QMessageBox.critical(self,'Return blocked',str(exc))
 def _pick_event(self,title):
  with self.database.connect() as c: events=c.execute("SELECT event_id,event_type FROM event_identity ORDER BY committed_at").fetchall()
  d=QDialog(self); d.setWindowTitle(title); f=QFormLayout(d); combo=QComboBox(); [combo.addItem(f"{r['event_type']} — {r['event_id']}",r['event_id']) for r in events]; evidence=QLineEdit('Verified corrective evidence'); f.addRow('Target Authoritative Event',combo); f.addRow('Corrective Evidence',evidence); b=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); b.accepted.connect(d.accept); b.rejected.connect(d.reject); f.addRow(b)
  return (combo.currentData(),evidence.text().strip()) if d.exec()==QDialog.DialogCode.Accepted else (None,None)
 def correction(self):
  target,evidence=self._pick_event('Correction Authority')
  if not target:return
  op=str(uuid4())
  try: self.services.correction.execute(request_id=f'{op}:correction',correction_event_id=f'COR-{op}',original_event_id=target,corrective_evidence=evidence); self.refresh(); QMessageBox.information(self,'Correction verified','Original event immutable. Append-only corrective lineage verified.')
  except Exception as exc: self.refresh(); QMessageBox.critical(self,'Correction blocked',str(exc))
 def reversal(self):
  target,_=self._pick_event('Reversal Authority')
  if not target:return
  op=str(uuid4())
  try: self.services.reversal.execute(request_id=f'{op}:reversal',reversal_event_id=f'REV-{op}',original_event_id=target); self.refresh(); QMessageBox.information(self,'Reversal verified','Original event immutable. Append-only reversal lineage verified.')
  except Exception as exc: self.refresh(); QMessageBox.critical(self,'Reversal blocked',str(exc))
