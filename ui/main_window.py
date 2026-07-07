from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,db,services):
  super().__init__(); self.db,self.services=db,services; self.setWindowTitle('MarketDEX OS — M32.B1'); self.resize(1380,780)
  root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1)
  title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title); lay.addWidget(QLabel('OPERATIONAL INVENTORY AUTHORITY INTEGRATION + CONTRACT CONFORMANCE')); lay.addWidget(QLabel('M29 DAMAGE / LOSS → M30 ALLOCATION → SALE → M31 CROSS-CHECK → LEDGER → REPLAY → RESTART'))
  self.run=QPushButton('Run Clean M32 Operational Inventory Acceptance Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run)
  self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table); self.footer=QLabel(); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root); self.refresh()
 def refresh(self):
  try:r=self.services.m32.verify()
  except Exception:r={'quantity':0,'active':0,'available':0,'ledger':'PENDING','replay':'PENDING','restart':'PENDING','integrity':'PENDING','damage':'PENDING','loss':'PENDING','oversell':'PENDING','release':'PENDING','cancel':'PENDING','sold':'PENDING','recon':'PENDING'}
  done=r['integrity']=='OPERATIONAL INVENTORY VERIFIED'; checks=[('Authoritative quantity truth',done and r['quantity']==2,'accepted inventory_authority = 2'),('Available quantity derivation',done and r['available']==2,'quantity 2 - ACTIVE allocation 0 = 2'),('Damage allocation-capacity defense',r['damage']=='VERIFIED','DAMAGE 4 blocked; DAMAGE 1 controlled'),('Loss allocation-capacity defense',r['loss']=='VERIFIED','LOSS beyond available quantity blocked'),('Cross-channel oversell prevention',r['oversell']=='BLOCKED','TCGplayer allocation 3 blocked at available 2'),('Release restoration exactly-once',r['release']=='VERIFIED','release restores availability; replay ZERO effect'),('Cancellation contract preservation',r['cancel']=='VERIFIED','accepted M30 cancellation contract preserved'),('SOLD conversion no-double-decrement',r['sold']=='VERIFIED','sale decrements once; conversion ZERO second decrement'),('Reconciliation lifecycle cross-check',r['recon']=='VERIFIED','observed 2 = remaining 2; ZERO adjustment'),('Unified inventory ledger reconciliation',r['ledger']=='RECONCILED','opening 5 - DAMAGE 1 - sale 2 = 2'),('Persistent cross-workflow replay defense',r['replay']=='PASS','committed requests create ZERO second mutation'),('Restart-persistent operational inventory integrity',r['restart']=='PASS','persisted authority reconstructs same result')]
  self.table.setRowCount(len(checks))
  for i,(n,ok,e) in enumerate(checks):
   for j,v in enumerate((n,'VERIFIED' if ok else 'PENDING',e)):self.table.setItem(i,j,QTableWidgetItem(str(v)))
  passed=sum(ok for _,ok,_ in checks); self.footer.setText(f'M32 authority gates verified: {passed} / 12 — authoritative quantity: {r["quantity"]} — active allocation: {r["active"]} — available quantity: {r["available"]} — oversell: {r["oversell"]} — ledger: {r["ledger"]} — replay: {r["replay"]} — restart: {r["restart"]} — operational inventory authority remains append-only')
 def execute(self):
  try:
   r=self.services.m32.run(); self.refresh()
   if r['integrity']!='OPERATIONAL INVENTORY VERIFIED':raise RuntimeError('M32 operational inventory verification incomplete')
   QMessageBox.information(self,'M32.B1 RESULT','M32.B1 RESULT — OPERATIONAL INVENTORY AUTHORITY INTEGRATION + CONTRACT CONFORMANCE VERIFIED')
  except Exception as exc:self.refresh(); QMessageBox.critical(self,'M32 operational inventory authority blocked',str(exc))
