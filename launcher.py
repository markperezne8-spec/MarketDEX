import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from core.database_manager import DatabaseManager
from services.service_registry import ServiceRegistry
from ui.main_window import MainWindow
if __name__=='__main__':
 db=DatabaseManager(Path(__file__).parent/'data'/'marketdex.sqlite3'); db.initialize(); services=ServiceRegistry(db); app=QApplication(sys.argv); w=MainWindow(db,services); w.show(); sys.exit(app.exec())
