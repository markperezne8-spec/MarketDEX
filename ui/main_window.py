from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout
class MainWindow(QMainWindow):
 def __init__(self,service):
  super().__init__(); self.service=service; self.setWindowTitle('MarketDEX OS — M35.B1'); self.resize(1380,820); root=QWidget(); outer=QHBoxLayout(root); panel=QWidget(); panel.setMaximumWidth(760); lay=QVBoxLayout(panel); outer.addWidget(panel); outer.addStretch(1); title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title); lay.addWidget(QLabel('INVENTORY-TO-PRODUCT CANONICAL LINKAGE + PRODUCT-AWARE INVENTORY AUTHORITY')); lay.addWidget(QLabel('ASSET → CANONICAL PRODUCT → LINKAGE → QUANTITY → AVAILABILITY → REPLAY → RESTART')); self.run=QPushButton('Run Clean M35 Inventory-to-Product Linkage Acceptance Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run); self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table); self.footer=QLabel(); self.footer.setWordWrap(True); lay.addWidget(self.footer); self.setCentralWidget(root); self.refresh()
 def refresh(self,r=None):
  r=r or self.service.verify(); self.table.setRowCount(len(r['checks']))
  for i,(name,ok,evidence) in enumerate(r['checks']):
   for j,v in enumerate((name,'VERIFIED' if ok else 'PENDING',evidence)): self.table.setItem(i,j,QTableWidgetItem(str(v)))
  self.footer.setText(f'M35 authority gates verified: {r["passed"]} / 12 — asset: {r["asset"]} — canonical product: {r["product"]} — linkage identity: {"PERSISTENT" if r["lid"]!="PENDING" else "PENDING"} — conflicting product linkage: {r["conflict"]} — product authoritative quantity: {r["q"]} — product available quantity: {r["available"]} — inventory mutation: {r["mutation"]} — history: {r["history"]} — replay: {r["replay"]} — audit: {r["audit"]} — restart: {r["restart"]} — state: {r["state"]}')
 def execute(self):
  try:
   r=self.service.run_acceptance(); self.refresh(r)
   if r['passed']!=12: raise RuntimeError('M35 authority verification incomplete')
   QMessageBox.information(self,'M35.B1 RESULT','M35.B1 RESULT — INVENTORY-TO-PRODUCT CANONICAL LINKAGE + PRODUCT-AWARE INVENTORY AUTHORITY VERIFIED')
  except Exception as exc:self.refresh(); QMessageBox.critical(self,'M35 linkage blocked',str(exc))
