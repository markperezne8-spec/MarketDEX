from PySide6.QtWidgets import (
    QMainWindow,QWidget,QVBoxLayout,QHBoxLayout
)
from app.ui.app_shell.header import Header
from app.ui.app_shell.sidebar import Sidebar
from app.ui.app_shell.workspace import Workspace
from app.ui.app_shell.right_panel import RightPanel
from app.ui.app_shell.footer import Footer

class AppShell(QMainWindow):
    """Permanent MarketDEX application shell."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarketDEX 1.0 Foundation")
        self.resize(1500,900)

        central = QWidget()
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0,0,0,0)

        root_layout.addWidget(Header())

        body = QHBoxLayout()
        body.addWidget(Sidebar(),1)
        body.addWidget(Workspace(),4)
        body.addWidget(RightPanel(),1)

        root_layout.addLayout(body)

        self.setCentralWidget(central)
        self.setStatusBar(Footer())
