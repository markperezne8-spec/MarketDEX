from PySide6.QtWidgets import QApplication
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService
from ui.main_window import MainWindow
from ui.inventory_edit_feature import install_inventory_edit_feature


def test_edit_details_control_is_installed_and_readable(tmp_path):
    app = QApplication.instance() or QApplication([])
    database_path = tmp_path / 'marketdex.sqlite3'
    window = MainWindow(MissionControlService(database_path), InventoryAppService(database_path))
    install_inventory_edit_feature(window)
    window.resize(1200, 900)
    window.show()
    app.processEvents()

    button = window.edit_details_button
    header = window.view_button.parent().layout()
    assert button.objectName() == 'edit_details_button'
    assert button.text() == 'Edit Details'
    assert header.indexOf(button) >= 0
    assert not button.isHidden()
    assert button.minimumWidth() >= button.sizeHint().width()
    assert window.view_button.parent().maximumWidth() >= 1100

    window.close()
