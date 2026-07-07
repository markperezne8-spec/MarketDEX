import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from services.m38_acceptance_service import M38AcceptanceService
from ui.main_window import MainWindow

if __name__ == "__main__":
    acceptance_db = Path(__file__).parent / "data" / "m38_acceptance.sqlite3"
    svc = M38AcceptanceService(acceptance_db)
    app = QApplication(sys.argv)
    w = MainWindow(svc)
    w.show()
    sys.exit(app.exec())
