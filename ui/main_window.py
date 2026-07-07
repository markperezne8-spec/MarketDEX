from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,service):
  super().__init__(); self.service=service; self.setWindowTitle('MarketDEX OS — M44.A1'); self.resize(1380,820); root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1); title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title); lay.addWidget(QLabel('BUSINESS DECISION AUTHORITY')); lay.addWidget(QLabel('INTELLIGENCE_READY → BUSINESS DECISION RECONSTRUCTION → DECISION_READY')); self.run=QPushButton('Run Clean M44A Business Decision Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run); self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table); self.footer=QLabel('M44A acceptance ready — click Run to execute isolated business decision reconstruction.'); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root)
 def refresh(self,r=None):
  r=r or self.service.verify(); self.table.setRowCount(len(r['checks']))
  for i,(name,ok,evidence) in enumerate(r['checks']):
   for j,value in enumerate((name,'VERIFIED' if ok else 'BLOCKED',evidence)): self.table.setItem(i,j,QTableWidgetItem(str(value)))
  self.footer.setText(f'M44A authority gates verified: {r["passed"]} / 12 — intelligence: {r["intelligence"]} — decision: {r["decision"]} — decision code: {r["decision_code"]} — reason: {r["reason"]} — inventory mutation: {r["inventory"]} — second sale: {r["second_sale"]} — second financial: {r["second_financial"]} — second settlement: {r["second_settlement"]} — second closure: {r["second_closure"]} — second finalization: {r["second_finalization"]} — second recognition: {r["second_recognition"]} — second posting: {r["second_posting"]} — second balance: {r["second_balance"]} — second summary: {r["second_summary"]} — second intelligence: {r["second_intelligence"]} — second SOLD: {r["second_sold"]} — history: {r["history"]} — replay: {r["replay"]} — restart: {r["restart"]} — M44A result: {r["result"]}')
 def execute(self):
  try:
   r=self.service.execute(); self.refresh(r)
   if r['passed']!=12: raise RuntimeError('M44A authority verification incomplete')
   QMessageBox.information(self,'M44.A1 RESULT','M44.A1 RESULT — BUSINESS DECISION AUTHORITY VERIFIED')
  except Exception as exc: self.table.setRowCount(0); self.footer.setText('M44A acceptance blocked.'); QMessageBox.critical(self,'M44A business decision blocked',str(exc))
