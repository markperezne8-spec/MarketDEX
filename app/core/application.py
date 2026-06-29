import sys
from PySide6.QtWidgets import QApplication
from app.core.startup import startup
from app.ui.app_shell.app_shell import AppShell

def run():
    startup()
    app = QApplication(sys.argv)
    window = AppShell()
    window.show()
    sys.exit(app.exec())
