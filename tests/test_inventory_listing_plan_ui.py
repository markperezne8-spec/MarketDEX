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


def build_window(path):
    inventory = InventoryAppService(path)
    window = MainWindow(MissionControlService(path), inventory)
    install_inventory_sale_readiness_feature(window)
    install_inventory_profit_feature(window)
    install_inventory_price_guidance_feature(window)
    install_inventory_listing_workspace_feature(window)
    return window


def test_workspace_saves_and_restores_listing_plan(tmp_path):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / 'marketdex.sqlite3'
    inventory = InventoryAppService(path)
    inventory.add_asset(asset_id='asset-1', asset_name='Test ETB', asset_type='SEALED', quantity=1, total_cost_minor=5000, request_id='add-1')
    window = build_window(path)
    window.inventory_table.selectRow(0)
    window.inventory_marketplace.setCurrentText('EBAY')
    window.inventory_target_sale_price.setValue(82.50)
    window.inventory_fee_percent.setValue(14.0)
    window.inventory_shipping_cost.setValue(5.25)
    window.inventory_packaging_cost.setValue(1.10)
    window.inventory_target_roi.setValue(30.0)
    window.inventory_save_listing_plan.click()
    assert window.inventory_listing_plan_status.text() == 'LISTING PLAN: Saved.'
    window.close()

    reopened = build_window(path)
    reopened.inventory_table.selectRow(0)
    assert reopened.inventory_marketplace.currentText() == 'EBAY'
    assert reopened.inventory_target_sale_price.value() == 82.50
    assert reopened.inventory_fee_percent.value() == 14.0
    assert reopened.inventory_shipping_cost.value() == 5.25
    assert reopened.inventory_packaging_cost.value() == 1.10
    assert reopened.inventory_target_roi.value() == 30.0
    assert reopened.inventory_listing_plan_status.text() == 'LISTING PLAN: Saved plan restored.'
    reopened.close()
