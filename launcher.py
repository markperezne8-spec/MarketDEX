import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from services.m40b_acceptance_service import M40BAcceptanceService
from ui.main_window import MainWindow

if __name__ == "__main__":
    acceptance_db = Path(__file__).parent / "data" / "m40b_acceptance.sqlite3"
    svc = M40BAcceptanceService(acceptance_db)
    app = QApplication(sys.argv)
    w = MainWindow(svc)
    w.show()
    sys.exit(app.exec())
