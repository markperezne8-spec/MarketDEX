from PySide6.QtWidgets import QApplication
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService
from ui.main_window import MainWindow
from ui.inventory_edit_feature import install_inventory_edit_feature


def test_edit_details_control_is_installed_in_inventory_toolbar(tmp_path):
    app = QApplication.instance() or QApplication([])
    database_path = tmp_path / 'marketdex.sqlite3'
    window = MainWindow(MissionControlService(database_path), InventoryAppService(database_path))
    install_inventory_edit_feature(window)

    button = window.edit_details_button
    header = window.inventory_header
    header_widgets = [
        header.itemAt(index).widget()
        for index in range(header.count())
        if header.itemAt(index).widget() is not None
    ]
    assert button.objectName() == 'edit_details_button'
    assert button.text() == 'Edit Details'
    assert button in header_widgets
    assert header_widgets.index(button) < header_widgets.index(window.adjust_button)
    assert button.minimumWidth() > 0
    assert window.inventory_panel.maximumWidth() >= 1100

    window.close()
