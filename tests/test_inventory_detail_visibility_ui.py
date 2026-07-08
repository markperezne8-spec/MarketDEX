import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService


def test_selected_asset_shows_business_metadata(tmp_path):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / 'marketdex.sqlite3'
    inventory = InventoryAppService(path)
    inventory.add_asset(asset_id='asset-1', asset_name='Chaos Rising ETB', asset_type='SEALED', quantity=1, total_cost_minor=6500, request_id='add-1')
    inventory.update_business_details(asset_id='asset-1', purchase_date='2026-07-08', purchase_source='Target', storage_location='Shelf A', notes='Hold sealed', request_id='details-1')
    window = MainWindow(MissionControlService(path), inventory)
    window.inventory_table.selectRow(0)
    window.show_selected()
    text = window.asset_detail.text()
    assert '2026-07-08' in text
    assert 'Target' in text
    assert 'Shelf A' in text
    assert 'Hold sealed' in text
    window.close()
