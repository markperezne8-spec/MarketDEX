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
        self.table.setHorizontalHeaderLabels(["Acceptance Control", "Result", "Evidence"])
        self.table.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self.table)
        self.footer = QLabel()
        self.footer.setWordWrap(True)
        lay.addWidget(self.footer)
        self.setCentralWidget(root)
        self.footer.setText("M39A acceptance ready — click Run to execute the isolated standalone settlement workflow.")

    def refresh(self, r=None):
        r = r or self.service.verify()
        gate_evidence = {name: evidence for name, _, evidence in r["checks"]}
        rows = [
            ("SALE IDENTITY", r["sale_identity"], gate_evidence["Authoritative sale identity"]),
            ("SALE EVENT", r["sale_event"], "SALE"),
            ("SALE PLATFORM", r["platform"], "eBay"),
            ("M24 FINANCIAL TRUTH", r["financial"], "VERIFIED"),
            ("EXPECTED NET PROCEEDS", r["expected"], gate_evidence["Expected net proceeds authority"]),
            ("SETTLEMENT EVIDENCE", r["evidence"], gate_evidence["Settlement evidence validation"]),
            ("OBSERVED PAYOUT", "VERIFIED" if r["settlement"] == "SETTLED" else "BLOCKED", gate_evidence["Expected net proceeds authority"]),
            ("PLATFORM MATCH", r["platform"], "eBay = eBay"),
            ("SETTLEMENT REQUEST", "VERIFIED" if r["settlement"] == "SETTLED" else "BLOCKED", gate_evidence["Explicit settlement request + event identity"]),
            ("SETTLEMENT EXECUTION", r["settlement"], "SettlementService.execute_settlement"),
            ("SETTLED STATE", "VERIFIED" if r["settlement"] == "SETTLED" else "BLOCKED", r["settlement"]),
            ("INVENTORY MUTATION", r["inventory_mutation"], "quantity remains 1"),
            ("SECOND SALE", r["second_sale"], "exactly one sale"),
            ("SECOND FINANCIAL SALE EVENT", r["second_financial"], "exactly one M24 financial event"),
            ("SOLD CONVERSION", "NO SECOND" if r["second_sale"] == "NO" else "BLOCKED", "one accepted M30 conversion only"),
            ("ORDER CLOSURE", r["order_closure"], "ZERO ORDER_CLOSE"),
            ("HISTORY RESULT", "VERIFIED" if r["passed"] == 12 else "BLOCKED", "append-only"),
            ("REPLAY RESULT", r["replay"], "ZERO second authoritative mutation"),
            ("RESTART RESULT", r["restart"], "SETTLED reconstructed"),
            ("M39A RESULT", r["result"], f'{r["passed"]} / 12'),
        ]
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
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
