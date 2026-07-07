import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from services.m39a_acceptance_service import M39AAcceptanceService
from ui.main_window import MainWindow

if __name__ == "__main__":
    acceptance_db = Path(__file__).parent / "data" / "m39a_acceptance.sqlite3"
    svc = M39AAcceptanceService(acceptance_db)
    app = QApplication(sys.argv)
    w = MainWindow(svc)
    w.show()
    sys.exit(app.exec())
