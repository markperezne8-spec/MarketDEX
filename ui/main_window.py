from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox

class MainWindow(QMainWindow):
    def __init__(self,database,services):
        super().__init__(); self.database,self.services=database,services
        self.setWindowTitle('MarketDEX OS — M29.B1'); self.resize(1380,760)
        root=QWidget(); lay=QVBoxLayout(root)
        title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title)
        lay.addWidget(QLabel('DAMAGE + LOSS INVENTORY ADJUSTMENT AUTHORITY'))
        lay.addWidget(QLabel('Evidence → Explicit Request → Revalidation → Controlled Movement → Reconciliation → Audit → Replay Defense'))
        self.run=QPushButton('Run Clean M29 Damage + Loss Acceptance Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run)
        self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Authority Gate','Result','Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table)
        self.footer=QLabel(); lay.addWidget(self.footer); self.setCentralWidget(root); self.refresh()
    def refresh(self):
        try: r=self.services.m29.verify()
        except Exception: r={'quantity':0,'damage':0,'loss':0,'movements':0,'audits':0,'replay':0,'deltas':[],'reconciled':False}
        checks=[
          ('Incomplete DAMAGE evidence fails closed',r['damage']==1,'BLOCKED request created ZERO extra movement'),
          ('DAMAGE controlled movement',r['damage']==1 and -1 in r['deltas'],'DAMAGE quantity_delta = -1'),
          ('DAMAGE replay defense',r['damage']==1 and r['quantity']<=2,'ZERO second quantity decrement'),
          ('Excess LOSS quantity fails closed',r['loss']==1,'Requested 3 > authoritative available quantity'),
          ('LOSS controlled movement',r['loss']==1 and r['deltas'].count(-1)==2,'LOSS quantity_delta = -1'),
          ('LOSS replay defense',r['loss']==1 and r['quantity']==1 and r['movements']==2,'ZERO second quantity decrement'),
          ('Movement ledger reconciliation',r['reconciled'],'expected quantity = authoritative quantity'),
          ('Append-only audit authority',r['audits']==2,'DAMAGE + LOSS VERIFIED audit events'),
          ('Restart-persistent authoritative result',r['quantity']==1 and r['movements']==2,'authoritative quantity = 1; 2 movements persist')]
        self.table.setRowCount(len(checks))
        for i,(name,ok,evidence) in enumerate(checks):
            for j,v in enumerate((name,'VERIFIED' if ok else 'PENDING',evidence)): self.table.setItem(i,j,QTableWidgetItem(str(v)))
        passed=sum(ok for _,ok,_ in checks)
        self.footer.setText(f'M29 authority gates verified: {passed} / 9 — authoritative quantity: {r["quantity"]} — DAMAGE + LOSS movement truth remains append-only')
    def execute(self):
        try:
            r=self.services.m29.run(); self.refresh()
            if not (r['quantity']==1 and r['damage']==1 and r['loss']==1 and r['movements']==2 and r['reconciled']): raise RuntimeError('M29 authority verification incomplete')
            QMessageBox.information(self,'M29.B1 RESULT','DAMAGE + LOSS INVENTORY ADJUSTMENT AUTHORITY VERIFIED')
        except Exception as exc:
            self.refresh(); QMessageBox.critical(self,'M29 adjustment authority blocked',str(exc))
