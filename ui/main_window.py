from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,service):
  super().__init__(); self.service=service; self.setWindowTitle('MarketDEX OS — M42.A1'); self.resize(1380,820); root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1); title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title); lay.addWidget(QLabel('BUSINESS PERFORMANCE SUMMARY AUTHORITY')); lay.addWidget(QLabel('BALANCED → BUSINESS PERFORMANCE RECONSTRUCTION → SUMMARIZED')); self.run=QPushButton('Run Clean M42A Business Performance Summary Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run); self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table); self.footer=QLabel('M42A acceptance ready — click Run to execute isolated business performance reconstruction.'); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root)
 def refresh(self,r=None):
  r=r or self.service.verify(); self.table.setRowCount(len(r['checks']))
  for i,(name,ok,evidence) in enumerate(r['checks']):
   for j,value in enumerate((name,'VERIFIED' if ok else 'BLOCKED',evidence)): self.table.setItem(i,j,QTableWidgetItem(str(value)))
  self.footer.setText(f'M42A authority gates verified: {r["passed"]} / 12 — balance: {r["balance"]} — summary: {r["summary"]} — sale count: {r["sale_count"]} — revenue: {r["revenue"]} — COGS: {r["cogs"]} — realized profit: {r["profit"]} — account: {r["account"]} — inventory mutation: {r["inventory"]} — second sale: {r["second_sale"]} — second financial: {r["second_financial"]} — second settlement: {r["second_settlement"]} — second closure: {r["second_closure"]} — second finalization: {r["second_finalization"]} — second recognition: {r["second_recognition"]} — second posting: {r["second_posting"]} — second balance: {r["second_balance"]} — second SOLD: {r["second_sold"]} — history: {r["history"]} — replay: {r["replay"]} — restart: {r["restart"]} — M42A result: {r["result"]}')
 def execute(self):
  try:
   r=self.service.execute(); self.refresh(r)
   if r['passed']!=12: raise RuntimeError('M42A authority verification incomplete')
   QMessageBox.information(self,'M42.A1 RESULT','M42.A1 RESULT — BUSINESS PERFORMANCE SUMMARY AUTHORITY VERIFIED')
  except Exception as exc: self.table.setRowCount(0); self.footer.setText('M42A acceptance blocked.'); QMessageBox.critical(self,'M42A performance summary blocked',str(exc))
