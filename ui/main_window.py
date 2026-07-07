from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QGridLayout,QGroupBox,QHBoxLayout


class MainWindow(QMainWindow):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.setWindowTitle('MarketDEX OS — Mission Control')
        self.resize(1480, 860)

        root = QWidget()
        outer = QHBoxLayout(root)
        panel = QWidget()
        panel.setMaximumWidth(760)
        layout = QVBoxLayout(panel)
        outer.addWidget(panel)
        outer.addStretch(1)

        title = QLabel('MarketDEX OS')
        title.setStyleSheet('font-size:36px;font-weight:700')
        layout.addWidget(title)
        subtitle = QLabel('MISSION CONTROL — LIVE SQLITE BUSINESS SNAPSHOT')
        subtitle.setStyleSheet('font-size:15px;font-weight:600')
        layout.addWidget(subtitle)

        self.values = {}
        grid = QGridLayout()
        cards = (
            ('📦 Inventory Units', 'inventory_units'),
            ('🗂️ Inventory Assets', 'inventory_asset_count'),
            ('💰 Inventory Cost', 'inventory_cost_minor'),
            ('🧾 Completed Sales', 'completed_sales'),
            ('📈 Revenue', 'revenue_minor'),
            ('💵 Profit', 'profit_minor'),
            ('🛡️ Verified Audits', 'verified_audits'),
            ('⚙️ Authority Events', 'authority_events'),
        )
        for index, (label, key) in enumerate(cards):
            box = QGroupBox(label)
            box_layout = QVBoxLayout(box)
            value = QLabel('--')
            value.setStyleSheet('font-size:24px;font-weight:700')
            box_layout.addWidget(value)
            self.values[key] = value
            grid.addWidget(box, index // 2, index % 2)
        layout.addLayout(grid)

        self.refresh_button = QPushButton('Refresh Mission Control')
        self.refresh_button.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_button)
        self.footer = QLabel('Loading MarketDEX business authority...')
        self.footer.setWordWrap(True)
        layout.addWidget(self.footer)
        layout.addStretch(1)
        self.setCentralWidget(root)
        self.refresh()

    @staticmethod
    def _money(minor):
        return f'${minor / 100:,.2f}'

    def refresh(self):
        snapshot = self.service.snapshot()
        for key in ('inventory_units','inventory_asset_count','completed_sales','verified_audits','authority_events'):
            self.values[key].setText(f'{snapshot[key]:,}')
        for key in ('inventory_cost_minor','revenue_minor','profit_minor'):
            self.values[key].setText(self._money(snapshot[key]))
        self.footer.setText(f"LIVE DATABASE: {snapshot['database_path']} — refreshed from protected SQLite authority.")
