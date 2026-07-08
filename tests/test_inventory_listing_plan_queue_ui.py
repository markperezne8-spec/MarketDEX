import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService
from ui.main_window import MainWindow
from ui.inventory_sale_readiness_feature import install_inventory_sale_readiness_feature
from ui.inventory_profit_feature import install_inventory_profit_feature
from ui.inventory_price_guidance_feature import install_inventory_price_guidance_feature
from ui.inventory_listing_workspace_feature import install_inventory_listing_workspace_feature
from ui.inventory_listing_plan_queue_feature import install_inventory_listing_plan_queue_feature


def test_saved_plan_enters_queue_and_reopens_asset(tmp_path):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / 'marketdex.sqlite3'
    inventory = InventoryAppService(path)
    inventory.add_asset(asset_id='asset-1', asset_name='Test ETB', asset_type='SEALED', quantity=1, total_cost_minor=10000, request_id='add-1')
    window = MainWindow(MissionControlService(path), inventory)
    install_inventory_sale_readiness_feature(window)
    install_inventory_profit_feature(window)
    install_inventory_price_guidance_feature(window)
    install_inventory_listing_workspace_feature(window)
    install_inventory_listing_plan_queue_feature(window)
    window.inventory_table.selectRow(0)
    window.inventory_target_sale_price.setValue(157.50)
    window.inventory_save_listing_plan.click()
    assert window.inventory_listing_plan_queue_table.rowCount() == 1
    assert window.inventory_listing_plan_queue_table.item(0, 0).text() == 'Test ETB'
    assert window.inventory_listing_plan_queue_table.item(0, 2).text() == '$157.50'
    window.inventory_table.clearSelection()
    window.inventory_listing_plan_queue_table.selectRow(0)
    window.inventory_open_listing_plan.click()
    assert window.selected_asset_id() == 'asset-1'
    window.close()
