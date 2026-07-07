from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,service):
  super().__init__(); self.service=service; self.setWindowTitle('MarketDEX OS — M51-M55 ADAPTIVE'); self.resize(1480,860); root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(900); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1); title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title); lay.addWidget(QLabel('ADAPTIVE FEEDBACK AUTHORITY CHAIN')); lay.addWidget(QLabel('FEEDBACK_READY → OUTCOME_READY → VARIANCE_READY → ADJUSTMENT_READY → ADAPTIVE_COMMAND_READY → ADAPTIVE_OPERATING_READY')); self.run=QPushButton('Run Clean M51-M55 Adaptive Feedback Authority Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run); self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table); self.footer=QLabel('M51-M55 desktop acceptance ready — click Run to execute the protected adaptive feedback chain.'); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root)
 def refresh(self,r=None):
  r=r or self.service.verify(); self.table.setRowCount(len(r['checks']))
  for i,(name,ok,evidence) in enumerate(r['checks']):
   for j,value in enumerate((name,'VERIFIED' if ok else 'BLOCKED',evidence)): self.table.setItem(i,j,QTableWidgetItem(str(value)))
  self.footer.setText(f'M51-M55 authority gates verified: {r["passed"]} / {r["gate_count"]} — adaptive state: {r["adaptive_state"]} — adaptive code: {r["adaptive_code"]} — history: {r["history"]} — replay: {r["replay"]} — restart: {r["restart"]} — result: {r["result"]}')
 def execute(self):
  try:
   r=self.service.execute(); self.refresh(r)
   if r['passed']!=r['gate_count']: raise RuntimeError('M51-M55 cumulative authority verification incomplete')
   QMessageBox.information(self,'M51-M55 RESULT','M51-M55 RESULT — ADAPTIVE FEEDBACK AUTHORITY CHAIN VERIFIED')
  except Exception as exc: self.table.setRowCount(0); self.footer.setText('M51-M55 cumulative acceptance blocked.'); QMessageBox.critical(self,'M51-M55 adaptive feedback chain blocked',str(exc))
