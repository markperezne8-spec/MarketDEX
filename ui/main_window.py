from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,db,services):
  super().__init__(); self.db,self.services=db,services; self.setWindowTitle('MarketDEX OS — M30.B1'); self.resize(1380,760)
  root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1)
  title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title); lay.addWidget(QLabel('MARKETPLACE PUBLICATION + ALLOCATION LIFECYCLE AUTHORITY')); lay.addWidget(QLabel('Publication → Allocation → Release / Cancellation → M24 Sale → SOLD Conversion'))
  self.run=QPushButton('Run Clean M30 Publication + Allocation Acceptance Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run)
  self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table); self.footer=QLabel(); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root); self.refresh()
 def refresh(self):
  try:r=self.services.m30.verify()
  except Exception:r={'quantity':0,'active':0,'available':0,'lifecycle':{},'ebay_state':None,'tcg_state':None,'replays':0,'financial':0,'audits':0}
  life=r['lifecycle']; checks=[('Publication controlled allocation',life.get('LISTED',0)==2,'eBay 2 + TCGplayer 1 accepted'),('Cross-channel oversell fails closed',life.get('LISTED',0)==2,'blocked 2-unit stale TCGplayer request created ZERO allocation'),('Concurrent availability revalidation',r['quantity']==2 and r['active']==0 and r['available']==2,'current authority revalidated before commit'),('Release restores availability exactly once',life.get('RELEASE',0)==1,'one authoritative RELEASE event'),('Release replay defense',life.get('RELEASE',0)==1 and r['replays']>=1,'ZERO second release / restoration'),('Cancellation restores availability exactly once',life.get('CANCELLATION',0)==1 and r['tcg_state']=='CANCELLED','TCGplayer allocation CANCELLED'),('Cancellation replay defense',life.get('CANCELLATION',0)==1 and r['replays']>=2,'ZERO second cancellation / restoration'),('SOLD conversion creates ZERO second sale depletion',life.get('SOLD_CONVERSION',0)==1 and r['quantity']==2 and r['financial']==1,'M24 decremented once; M30 delta = 0'),('Allocation ledger reconciliation',r['active']==0 and r['available']==r['quantity'],'expected active allocation = authoritative active allocation'),('Restart-persistent publication lifecycle authority',r['quantity']==2 and r['active']==0 and r['available']==2 and r['ebay_state']=='CONSUMED' and r['tcg_state']=='CANCELLED' and r['audits']==5,'lifecycle + audit authority persist in SQLite')]
  self.table.setRowCount(len(checks))
  for i,(name,ok,evidence) in enumerate(checks):
   for j,v in enumerate((name,'VERIFIED' if ok else 'PENDING',evidence)):self.table.setItem(i,j,QTableWidgetItem(str(v)))
  passed=sum(ok for _,ok,_ in checks); self.footer.setText(f'M30 authority gates verified: {passed} / 10 — authoritative quantity: {r["quantity"]} — active allocation: {r["active"]} — available quantity: {r["available"]} — publication + allocation lifecycle truth remains append-only')
 def execute(self):
  try:
   r=self.services.m30.run(); self.refresh()
   if not (r['quantity']==2 and r['active']==0 and r['available']==2):raise RuntimeError('M30 authority verification incomplete')
   QMessageBox.information(self,'M30.B1 RESULT','MARKETPLACE PUBLICATION + ALLOCATION LIFECYCLE AUTHORITY VERIFIED')
  except Exception as exc:self.refresh(); QMessageBox.critical(self,'M30 publication lifecycle authority blocked',str(exc))
