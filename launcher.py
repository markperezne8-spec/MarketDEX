import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from services.m51_m55_desktop_acceptance_service import M51M55DesktopAcceptanceService
from ui.main_window import MainWindow

if __name__ == "__main__":
    acceptance_db = Path(__file__).parent / "data" / "m51_m55_acceptance.sqlite3"
    svc = M51M55DesktopAcceptanceService(acceptance_db)
    app = QApplication(sys.argv)
    w = MainWindow(svc)
    w.show()
    sys.exit(app.exec())
