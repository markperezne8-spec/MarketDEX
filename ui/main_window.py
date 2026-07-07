from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,service):
  super().__init__(); self.service=service; self.setWindowTitle('MarketDEX OS — M45-M49 ACCELERATED'); self.resize(1480,860); root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(860); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1); title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title); lay.addWidget(QLabel('ACCELERATED OPERATING COMMAND AUTHORITY CHAIN')); lay.addWidget(QLabel('DECISION_READY → ACTION_PLAN_READY → PRIORITIZED → EXECUTION_READY → COMMAND_READY → OPERATING_READY')); self.run=QPushButton('Run Clean M45-M49 Accelerated Operating Command Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run); self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table); self.footer=QLabel('M45-M49 cumulative acceptance ready — click Run to execute the protected operating-command chain.'); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root)
 def refresh(self,r=None):
  r=r or self.service.verify(); self.table.setRowCount(len(r['checks']))
  for i,(name,ok,evidence) in enumerate(r['checks']):
   for j,value in enumerate((name,'VERIFIED' if ok else 'BLOCKED',evidence)): self.table.setItem(i,j,QTableWidgetItem(str(value)))
  self.footer.setText(f'M45-M49 authority gates verified: {r["passed"]} / 20 — operating state: {r["operating_state"]} — operating code: {r["operating_code"]} — inventory mutation: {r["inventory"]} — history: {r["history"]} — replay: {r["replay"]} — restart: {r["restart"]} — result: {r["result"]}')
 def execute(self):
  try:
   r=self.service.execute(); self.refresh(r)
   if r['passed']!=20: raise RuntimeError('M45-M49 cumulative authority verification incomplete')
   QMessageBox.information(self,'M45-M49 RESULT','M45-M49 RESULT — ACCELERATED OPERATING COMMAND CHAIN VERIFIED')
  except Exception as exc: self.table.setRowCount(0); self.footer.setText('M45-M49 cumulative acceptance blocked.'); QMessageBox.critical(self,'M45-M49 operating command chain blocked',str(exc))
