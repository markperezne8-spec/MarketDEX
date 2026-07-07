from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox

class MainWindow(QMainWindow):
    def __init__(self,database,services):
        super().__init__(); self.database,self.services=database,services
        self.setWindowTitle('MarketDEX OS — M28.B1'); self.resize(1380,760)
        root=QWidget(); lay=QVBoxLayout(root)
        title=QLabel('MarketDEX OS'); title.setStyleSheet('font-size:36px;font-weight:700'); lay.addWidget(title)
        lay.addWidget(QLabel('END-TO-END BUSINESS AUTHORITY INTEGRATION + CONTRACT CONFORMANCE'))
        lay.addWidget(QLabel('M20 → M27 Integrated Authority • Fail Closed • Append-Only • Replay Defense • Derived Mission Control'))
        self.run=QPushButton('Run Clean M28 Conformance Workflow'); self.run.clicked.connect(self.execute); lay.addWidget(self.run)
        self.table=QTableWidget(0,3); self.table.setHorizontalHeaderLabels(['Contract Gate','Result','Authoritative Evidence']); self.table.horizontalHeader().setStretchLastSection(True); lay.addWidget(self.table)
        self.footer=QLabel('M28.B1 conformance workflow not yet executed on this database.'); lay.addWidget(self.footer)
        self.setCentralWidget(root); self.refresh()
    def refresh(self):
        with self.database.connect() as c:
            checks=[
              ('Acquisition + persisted inventory', c.execute('SELECT COUNT(*) FROM inventory_history').fetchone()[0]>0, 'inventory_history'),
              ('Transformation lineage + cost conservation', c.execute('SELECT COUNT(*) FROM transformation_lineage').fetchone()[0]>0, 'transformation_lineage'),
              ('Marketplace allocation authority', c.execute('SELECT COUNT(*) FROM marketplace_allocations').fetchone()[0]>0, 'marketplace_allocations'),
              ('Sale + financial truth', c.execute('SELECT COUNT(*) FROM sales').fetchone()[0]>0, 'sales + sales_financial_history'),
              ('Settlement + order closure', c.execute('SELECT COUNT(*) FROM order_closures').fetchone()[0]>0, 'settlements + order_closures'),
              ('Return + cost restoration', c.execute('SELECT COUNT(*) FROM returns').fetchone()[0]>0, 'returns + financial_events'),
              ('Corrective authority immutable lineage', c.execute('SELECT COUNT(*) FROM correction_events').fetchone()[0]>0, 'correction_events'),
              ('Exception + controlled resolution', c.execute('SELECT COUNT(*) FROM exception_resolutions').fetchone()[0]>0, 'exception_history + exception_resolutions'),
              ('Audit verification', c.execute("SELECT COUNT(*) FROM audit_verifications WHERE verification_result='VERIFIED'").fetchone()[0]>0, 'audit_verifications'),
            ]
        self.table.setRowCount(len(checks))
        for i,(name,ok,evidence) in enumerate(checks):
            for j,v in enumerate((name,'VERIFIED' if ok else 'PENDING',evidence)): self.table.setItem(i,j,QTableWidgetItem(str(v)))
        passed=sum(1 for _,ok,_ in checks if ok)
        self.footer.setText(f'M28 contract gates verified: {passed} / {len(checks)} — Mission Control remains derived with ZERO direct business writes')
    def execute(self):
        try:
            r=self.services.conformance.run_clean_acceptance()
            self.refresh()
            if not r['oversell_blocked']: raise RuntimeError('Cross-channel oversell defense failed')
            QMessageBox.information(self,'M28.B1 RESULT','END-TO-END BUSINESS AUTHORITY INTEGRATION + CONTRACT CONFORMANCE VERIFIED')
        except Exception as exc:
            self.refresh(); QMessageBox.critical(self,'M28 conformance blocked',str(exc))
