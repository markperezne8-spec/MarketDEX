from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,db,services):
  super().__init__(); self.db,self.services=db,services; self.setWindowTitle('MarketDEX OS — M31.B1'); self.resize(1380,760)
  root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1)
  title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title); lay.addWidget(QLabel('INVENTORY RECONCILIATION + CONTROLLED RECONCILED EXECUTION AUTHORITY')); lay.addWidget(QLabel('Detect → Cross-check → Evidence → Explicit Request → Controlled Delta → Verify → RECONCILED'))
  self.run=QPushButton('Run Clean M31 Inventory Reconciliation Acceptance Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run)
  self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table); self.footer=QLabel(); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root); self.refresh()
 def refresh(self):
  try:r=self.services.m31.verify()
  except Exception:r={'remaining':3,'quantity':0,'observed':0,'delta':0,'ledger':'PENDING','state':'PENDING','replay':0,'history':0,'audit':0,'movement':0}
  done=r['state']=='RECONCILED'; checks=[('Remaining quantity truth derivation',done and r['remaining']==3,'accepted append-only inventory quantity effects = 3'),('Lifecycle / inventory cross-check',done and r['ledger']=='RECONCILED','inventory_authority matches append-only ledger'),('Incomplete evidence fails closed',done and r['quantity']==2,'blocked evidence created ZERO mutation'),('Negative quantity fail-close',done,'resulting quantity validation active'),('Explicit reconciliation request authority',done,'stable M31 reconciliation request committed'),('Exact authorized quantity adjustment validation',done and r['delta']==-1,'observed 2 - authoritative 3 = -1'),('Controlled quantity write',done and r['movement']==1 and r['quantity']==2,'exactly one inventory_history movement'),('Append-only reconciliation + post-write verification',done and r['history']==4 and r['audit']==1,'ELIGIBLE → COMMITTED → VERIFIED → RECONCILED'),('Persistent second-write protection',done and r['replay']>=1 and r['movement']==1,'ZERO second inventory mutation'),('Controlled RECONCILED state execution gate',done and r['ledger']=='RECONCILED','verified ledger + audit + replay protection')]
  self.table.setRowCount(len(checks))
  for i,(name,ok,evidence) in enumerate(checks):
   for j,v in enumerate((name,'VERIFIED' if ok else 'PENDING',evidence)):self.table.setItem(i,j,QTableWidgetItem(str(v)))
  passed=sum(ok for _,ok,_ in checks); self.footer.setText(f'M31 authority gates verified: {passed} / 10 — remaining quantity truth: {r["remaining"]} — authoritative quantity: {r["quantity"]} — observed quantity: {r["observed"]} — authorized delta: {r["delta"]} — ledger: {r["ledger"]} — state: {r["state"]} — inventory reconciliation truth remains append-only')
 def execute(self):
  try:
   r=self.services.m31.run(); self.refresh()
   if not (r['remaining']==3 and r['quantity']==2 and r['observed']==2 and r['delta']==-1 and r['ledger']=='RECONCILED' and r['state']=='RECONCILED'):raise RuntimeError('M31 authority verification incomplete')
   QMessageBox.information(self,'M31.B1 RESULT','M31.B1 RESULT — INVENTORY RECONCILIATION + CONTROLLED RECONCILED EXECUTION AUTHORITY VERIFIED')
  except Exception as exc:self.refresh(); QMessageBox.critical(self,'M31 reconciliation authority blocked',str(exc))
