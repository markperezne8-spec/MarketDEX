from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
)
from app.ui.app_shell.header import Header
from app.ui.app_shell.sidebar import Sidebar
from app.ui.app_shell.workspace import Workspace
from app.ui.app_shell.right_panel import RightPanel
from app.ui.app_shell.footer import Footer


class AppShell(QMainWindow):
    """
    Main application window and component coordinator for MarketDEX.
    
    Responsible for:
    - Creating the main window layout
    - Instantiating all UI components
    - Wiring navigation signals from Sidebar to Workspace
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarketDEX 1.0 Foundation")
        self.resize(1500, 900)

        # Create central widget and root layout
        central = QWidget()
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Add header
        root_layout.addWidget(Header())

        # Create body layout with sidebar, workspace, and right panel
        body = QHBoxLayout()

        # Create Workspace first (as the state holder)
        self.workspace = Workspace()

        # Create Sidebar (independent component)
        self.sidebar = Sidebar()

        # CONNECT: Wire sidebar navigation signal to workspace slot
        # When user clicks sidebar button, it emits navigation_requested(page_id)
        # This signal is connected to workspace.show_page(page_id)
        self.sidebar.navigation_requested.connect(self.workspace.show_page)

        # Add components to body layout with proportions
        body.addWidget(self.sidebar, 1)      # Sidebar: 1/6 of width
        body.addWidget(self.workspace, 4)    # Workspace: 4/6 of width
        body.addWidget(RightPanel(), 1)      # RightPanel: 1/6 of width

        root_layout.addLayout(body)

        # Set central widget
        self.setCentralWidget(central)

        # Set status bar (footer)
        self.setStatusBar(Footer())
