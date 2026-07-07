from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout
)


class MainWindow(QMainWindow):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.setWindowTitle("MarketDEX OS â€” M38.B1")
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
        lay.addWidget(QLabel("PRODUCT-AWARE MARKETPLACE SALE EXECUTION + M24 SALES AUTHORITY INTEGRATION"))
        lay.addWidget(QLabel("PRODUCT â†’ ASSET â†’ LISTING â†’ PUBLICATION â†’ ALLOCATION â†’ M24 SALE â†’ M30 SOLD"))
        self.run = QPushButton("Run Clean M38 Product-Aware Sale Acceptance Workflow")
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
        self.table.setRowCount(0)
        self.footer.setText("M38 acceptance ready - click Run to execute the isolated product-aware sale workflow.")

    def refresh(self, r=None):
        r = r or self.service.verify()
        self.table.setRowCount(len(r["checks"]))
        for i, (name, ok, evidence) in enumerate(r["checks"]):
            for j, value in enumerate((name, "VERIFIED" if ok else "PENDING", evidence)):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
        self.footer.setText(
            f'M38 authority gates verified: {r["passed"]} / 12 â€” product lineage: {r["product"]} '
            f'â€” listing: {r["listing"]} â€” publication: {r["publication"]} â€” allocation: {r["allocation"]} '
            f'â€” M24 sale: {r["sale"]} â€” inventory depletion: {r["inventory"]} '
            f'â€” financial truth: {r["financial"]} â€” second financial event: {r["second_financial"]} '
            f'â€” replay: {r["replay"]} â€” restart: {r["restart"]} â€” M38 result: {r["result"]}'
        )

    def execute(self):
        try:
            r = self.service.execute()
            self.refresh(r)
            if r["passed"] != 12:
                raise RuntimeError("M38 authority verification incomplete")
            QMessageBox.information(
                self,
                "M38.B1 RESULT",
                "M38.B1 RESULT â€” PRODUCT-AWARE MARKETPLACE SALE EXECUTION + M24 SALES AUTHORITY INTEGRATION VERIFIED",
            )
        except Exception as exc:
            self.table.setRowCount(0)
            self.footer.setText("M38 acceptance blocked.")
            QMessageBox.critical(self, "M38 sale execution blocked", str(exc))
