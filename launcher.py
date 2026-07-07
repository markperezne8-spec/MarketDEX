import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from services.m44a_acceptance_service import M44AAcceptanceService
from ui.main_window import MainWindow

if __name__ == "__main__":
    acceptance_db = Path(__file__).parent / "data" / "m44a_acceptance.sqlite3"
    svc = M44AAcceptanceService(acceptance_db)
    app = QApplication(sys.argv)
    w = MainWindow(svc)
    w.show()
    sys.exit(app.exec())
