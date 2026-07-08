import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from services.mission_control_service import MissionControlService
from services.inventory_app_service import InventoryAppService
from ui.main_window import MainWindow
from ui.inventory_edit_feature import install_inventory_edit_feature


if __name__ == '__main__':
    database_path = Path(__file__).parent / 'data' / 'm51_m55_acceptance.sqlite3'
    mission_control = MissionControlService(database_path)
    inventory = InventoryAppService(database_path)
    app = QApplication(sys.argv)
    window = MainWindow(mission_control, inventory)
    install_inventory_edit_feature(window)
    window.show()
    sys.exit(app.exec())
