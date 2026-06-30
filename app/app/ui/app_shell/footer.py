from PySide6.QtWidgets import QStatusBar
class Footer(QStatusBar):
    def __init__(self):
        super().__init__()
        self.showMessage("Ready | SQLite: Pending | v1.0 Foundation")
