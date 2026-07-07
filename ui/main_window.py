from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,service):
  super().__init__(); self.service=service; self.setWindowTitle('MarketDEX OS — M33.B1'); self.resize(1380,780)
  root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1)
  title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title); lay.addWidget(QLabel('WORKBOOK-TO-DESKTOP AUTHORITY PARITY + MIGRATION COMPLETION FREEZE')); lay.addWidget(QLabel('WORKBOOK AUTHORITY → DESKTOP OWNER → CONTRACT → RESTART → REPLAY → MIGRATION COMPLETE'))
  self.run=QPushButton('Run Clean M33 Migration Parity Acceptance Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run)
  self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table); self.footer=QLabel(); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root); self.refresh()
 def refresh(self):
  r=self.service.verify(); self.table.setRowCount(len(r['checks']))
  for i,(name,ok,evidence) in enumerate(r['checks']):
   for j,v in enumerate((name,'VERIFIED' if ok else 'BLOCKED',evidence)): self.table.setItem(i,j,QTableWidgetItem(str(v)))
  self.footer.setText(f'M33 authority gates verified: {r["passed"]} / 12 — missing mappings: {r["missing"]} — duplicate owners: {r["duplicate"]} — parallel truth: {r["parallel"]} — unauthorized mutation paths: {r["unauthorized"]} — Mission Control write violations: {r["mc"]} — restart: {r["restart"]} — replay: {r["replay"]} — parity: {r["parity"]} — migration state: {r["state"]}')
 def execute(self):
  try:
   r=self.service.run(); self.refresh()
   if r['state']!='MIGRATION COMPLETE': raise RuntimeError('Migration completion BLOCKED')
   QMessageBox.information(self,'M33.B1 RESULT','M33.B1 RESULT — WORKBOOK-TO-DESKTOP AUTHORITY PARITY + MIGRATION COMPLETION FREEZE VERIFIED')
  except Exception as exc: self.refresh(); QMessageBox.critical(self,'M33 migration completion blocked',str(exc))
