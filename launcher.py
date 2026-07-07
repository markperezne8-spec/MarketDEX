import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from services.mission_control_service import MissionControlService
from ui.main_window import MainWindow


if __name__ == '__main__':
    database_path = Path(__file__).parent / 'data' / 'm51_m55_acceptance.sqlite3'
    service = MissionControlService(database_path)
    app = QApplication(sys.argv)
    window = MainWindow(service)
    window.show()
    sys.exit(app.exec())
