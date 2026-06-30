from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal
from app.ui.app_shell.navigation import SIDEBAR_PAGES


class Sidebar(QWidget):
    """
    Navigation sidebar for MarketDEX.
    
    Emits navigation_requested signal with page identifiers when buttons are clicked.
    Does not hold references to Workspace - remains independent.
    """

    # Signal: emits the page identifier (string) when a button is clicked
    navigation_requested = Signal(str)

    def __init__(self):
        super().__init__()
        
        self.setObjectName("Sidebar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a button for each navigation item
        for label, page_id in SIDEBAR_PAGES:
            btn = QPushButton(label)
            # Connect button click to emit signal with page identifier
            btn.clicked.connect(lambda checked=False, pid=page_id: self.navigation_requested.emit(pid))
            layout.addWidget(btn)
        
        # Add stretch to push buttons to top
        layout.addStretch()
