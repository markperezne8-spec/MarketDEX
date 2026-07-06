from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel

class MainWindow(QMainWindow):
    def __init__(self, database_path):
        super().__init__()
        self.setWindowTitle('MarketDEX OS — M20.B1')
        self.resize(900, 560)
        root = QWidget(); layout = QVBoxLayout(root)
        title = QLabel('MarketDEX OS'); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('font-size: 30px; font-weight: 700;')
        status = QLabel('DESKTOP FOUNDATION READY')
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet('font-size: 18px;')
        authority = QLabel('Persistence Authority • Event Identity • Service Boundaries')
        authority.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path = QLabel(f'Offline database initialized:\n{database_path}')
        path.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path.setWordWrap(True)
        layout.addStretch(); layout.addWidget(title); layout.addWidget(status); layout.addWidget(authority); layout.addWidget(path); layout.addStretch()
        self.setCentralWidget(root)
