import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.inventory_sale_readiness_feature import install_inventory_sale_readiness_feature
from ui.inventory_profit_feature import install_inventory_profit_feature
from ui.inventory_price_guidance_feature import install_inventory_price_guidance_feature, price_guidance
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService


def test_use_recommended_price_updates_target_sale_price(tmp_path):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / 'marketdex.sqlite3'; inventory = InventoryAppService(path)
    inventory.add_asset(asset_id='asset-1', asset_name='Test ETB', asset_type='SEALED', quantity=2, total_cost_minor=10000, request_id='add-1')
    window = MainWindow(MissionControlService(path), inventory)
    install_inventory_sale_readiness_feature(window); install_inventory_profit_feature(window); install_inventory_price_guidance_feature(window)
    window.inventory_table.selectRow(0); window.show_selected(); window.inventory_target_roi.setValue(40.0)
    expected = price_guidance(5000, window.inventory_fee_percent.value(), 0, 0, 40.0)['recommended_minor']
    window.inventory_use_recommended_price.click()
    assert round(window.inventory_target_sale_price.value() * 100) == expected
    window.close()
