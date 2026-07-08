from PySide6.QtWidgets import QApplication
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService
from ui.main_window import MainWindow
from ui.inventory_edit_feature import install_inventory_edit_feature


def test_edit_details_control_is_visible_and_readable(tmp_path):
    app = QApplication.instance() or QApplication([])
    database_path = tmp_path / 'marketdex.sqlite3'
    window = MainWindow(MissionControlService(database_path), InventoryAppService(database_path))
    install_inventory_edit_feature(window)
    window.show()
    app.processEvents()

    button = window.edit_details_button
    assert button.objectName() == 'edit_details_button'
    assert button.text() == 'Edit Details'
    assert button.isVisible()
    assert button.width() >= button.sizeHint().width()
    assert window.view_button.parent().maximumWidth() >= 1100

    window.close()
