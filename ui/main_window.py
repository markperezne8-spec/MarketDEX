from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout
)


class MainWindow(QMainWindow):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.setWindowTitle("MarketDEX OS — M39A.B1")
        self.resize(1380, 820)

        root = QWidget()
        outer = QHBoxLayout(root)
        panel = QWidget()
        panel.setMaximumWidth(760)
        lay = QVBoxLayout(panel)
        outer.addWidget(panel)
        outer.addStretch(1)

        title = QLabel("MarketDEX OS")
        title.setStyleSheet("font-size:36px;font-weight:700")
        lay.addWidget(title)
        lay.addWidget(QLabel("STANDALONE SETTLEMENT EXECUTION + SETTLED STATE AUTHORITY"))
        lay.addWidget(QLabel("SALE → M24 FINANCIAL TRUTH → PAYOUT EVIDENCE → SETTLEMENT → SETTLED"))
        self.run = QPushButton("Run Clean M39A Standalone Settlement Acceptance Workflow")
        self.run.clicked.connect(self.execute)
        lay.addWidget(self.run)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Authority Gate", "Result", "Evidence"])
        self.table.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self.table)
        self.footer = QLabel()
        self.footer.setWordWrap(True)
        lay.addWidget(self.footer)
        self.setCentralWidget(root)
        self.footer.setText("M39A acceptance ready — click Run to execute the isolated standalone settlement workflow.")

    def refresh(self, r=None):
        r = r or self.service.verify()
        self.table.setRowCount(len(r["checks"]))
        for i, (name, ok, evidence) in enumerate(r["checks"]):
            for j, value in enumerate((name, "VERIFIED" if ok else "BLOCKED", evidence)):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
        self.footer.setText(
            f'M39A authority gates verified: {r["passed"]} / 12 — sale identity: {r["sale_identity"]} '
            f'— sale event: {r["sale_event"]} — platform: {r["platform"]} '
            f'— M24 financial truth: {r["financial"]} — expected net proceeds: {r["expected"]} '
            f'— settlement evidence: {r["evidence"]} — settlement: {r["settlement"]} '
            f'— second sale: {r["second_sale"]} — inventory mutation: {r["inventory_mutation"]} '
            f'— second financial sale event: {r["second_financial"]} — order closure: {r["order_closure"]} '
            f'— replay: {r["replay"]} — restart: {r["restart"]} — M39A result: {r["result"]}'
        )

    def execute(self):
        try:
            r = self.service.execute()
            self.refresh(r)
            if r["passed"] != 12:
                raise RuntimeError("M39A authority verification incomplete")
            QMessageBox.information(
                self, "M39A.B1 RESULT",
                "M39A.B1 RESULT — STANDALONE SETTLEMENT EXECUTION + SETTLED STATE AUTHORITY VERIFIED",
            )
        except Exception as exc:
            self.table.setRowCount(0)
            self.footer.setText("M39A acceptance blocked.")
            QMessageBox.critical(self, "M39A settlement execution blocked", str(exc))
