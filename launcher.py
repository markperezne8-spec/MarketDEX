from pathlib import Path
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry
from ui.main_window import MainWindow

def main():
    root = Path(__file__).resolve().parent
    database = DatabaseManager(root / 'data' / 'marketdex.sqlite3')
    try:
        database.initialize()
        ServiceRegistry(database)
    except Exception as exc:
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, 'MarketDEX startup blocked', str(exc))
        return 1
    app = QApplication(sys.argv)
    window = MainWindow(database.database_path)
    window.show()
    return app.exec()

if __name__ == '__main__': raise SystemExit(main())
