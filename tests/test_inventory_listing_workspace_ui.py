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


def test_listing_workspace_reacts_to_connected_pricing_inputs(tmp_path):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / 'marketdex.sqlite3'; inventory = InventoryAppService(path)
    inventory.add_asset(asset_id='asset-1', asset_name='Test ETB', asset_type='SEALED', quantity=2, total_cost_minor=10000, request_id='add-1')
    window = MainWindow(MissionControlService(path), inventory)
    install_inventory_sale_readiness_feature(window); install_inventory_profit_feature(window); install_inventory_price_guidance_feature(window); install_inventory_listing_workspace_feature(window)
    window.inventory_table.selectRow(0); window.inventory_marketplace.setCurrentText('EBAY'); window.inventory_shipping_cost.setValue(5); window.inventory_packaging_cost.setValue(1); window.inventory_target_sale_price.setValue(80)
    text = window.inventory_listing_workspace_summary.text()
    assert 'Test ETB' in text and 'EBAY' in text and 'Net $13.40' in text and 'SALE READY' in text
    window.close()
