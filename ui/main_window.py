from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,service):
  super().__init__(); self.service=service; self.setWindowTitle('MarketDEX OS — M37.B1'); self.resize(1380,820)
  root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1)
  title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title)
  lay.addWidget(QLabel('LISTING-TO-PUBLICATION CONTROLLED EXECUTION + PRODUCT-AWARE M30 AUTHORITY INTEGRATION'))
  lay.addWidget(QLabel('READY LISTING → LISTED REQUEST → M30 PUBLICATION → ACTIVE ALLOCATION → REPLAY → RESTART'))
  self.run=QPushButton('Run Clean M37 Controlled Publication Acceptance Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run)
  self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table)
  self.footer=QLabel(); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root); self.refresh()
 def refresh(self,r=None):
  r=r or self.service.verify(); self.table.setRowCount(len(r['checks']))
  for i,(name,ok,evidence) in enumerate(r['checks']):
   for j,v in enumerate((name,'VERIFIED' if ok else 'PENDING',evidence)): self.table.setItem(i,j,QTableWidgetItem(str(v)))
  self.footer.setText(f'M37 authority gates verified: {r["passed"]} / 12 — M36 listing: {r["listing"]} — publication request: {r["request"]} — M30 publication: {r["publication"]} — allocation: {r["allocation"]} — lineage: {r["lineage"]} — product available quantity: {r["available"]} — second business mutation: {r["mutation"]} — history: {r["history"]} — replay: {r["replay"]} — audit: {r["audit"]} — restart: {r["restart"]} — state: {r["state"]}')
 def execute(self):
  try:
   r=self.service.execute(); self.refresh(r)
   if r['passed']!=12: raise RuntimeError('M37 authority verification incomplete')
   QMessageBox.information(self,'M37.B1 RESULT','M37.B1 RESULT — LISTING-TO-PUBLICATION CONTROLLED EXECUTION + PRODUCT-AWARE M30 AUTHORITY INTEGRATION VERIFIED')
  except Exception as exc:self.refresh(); QMessageBox.critical(self,'M37 publication blocked',str(exc))
