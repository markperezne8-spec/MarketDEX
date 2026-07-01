from PySide6.QtWidgets import QMainWindow,QWidget,QHBoxLayout
from app.ui.navigation import NavigationPanel
from app.ui.workspace import Workspace
from app.ui.status_bar import build_status_bar
from app.ui.menu_bar import build_menu

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarketDEX v0.1.0-alpha.1")
        self.resize(1280,800)
        build_menu(self)
        self.workspace=Workspace()
        self.navigation=NavigationPanel(self.workspace)
        central=QWidget()
        layout=QHBoxLayout(central)
        layout.addWidget(self.navigation)
        layout.addWidget(self.workspace,1)
        self.setCentralWidget(central)
        self.setStatusBar(build_status_bar(self))
