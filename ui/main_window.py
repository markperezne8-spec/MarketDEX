from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel

class MainWindow(QMainWindow):
    def __init__(self, database_path):
        super().__init__()
        self.setWindowTitle('MarketDEX OS — M21.B1')
        self.resize(900, 560)
        root = QWidget()
        layout = QVBoxLayout(root)
        labels = [
            ('MarketDEX OS', 30, True),
            ('PERSISTENCE AUTHORITY READY', 18, False),
            ('Repositories • Asset Authority • Inventory Authority', 14, False),
            ('Controlled Writes • Append-Only History • Replay Defense', 14, False),
            (f'Offline authority database:\n{database_path}', 12, False),
        ]
        layout.addStretch()
        for text, size, bold in labels:
            label = QLabel(text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet(f'font-size: {size}px;' + (' font-weight: 700;' if bold else ''))
            layout.addWidget(label)
        layout.addStretch()
        self.setCentralWidget(root)
