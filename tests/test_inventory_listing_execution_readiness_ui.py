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
from ui.inventory_listing_execution_readiness_feature import install_inventory_listing_execution_readiness_feature, listing_execution_readiness


def test_execution_readiness_contract():
    row = {'quantity': 1, 'total_cost_minor': 10000}
    plan = {'marketplace': 'eBay', 'target_sale_price_minor': 15750}
    result = listing_execution_readiness(row, plan)
    assert result['ready'] is True
    assert result['missing'] == []


def test_saved_plan_becomes_ready_to_prepare(tmp_path):
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
    install_inventory_listing_execution_readiness_feature(window)
    window.inventory_table.selectRow(0)
    window.inventory_target_sale_price.setValue(157.50)
    window.inventory_save_listing_plan.click()
    assert 'READY TO PREPARE' in window.inventory_listing_execution_readiness_summary.text()
    assert '✓ Quantity' in window.inventory_listing_execution_readiness_checklist.text()
    assert '✓ Sale Ready' in window.inventory_listing_execution_readiness_checklist.text()
    window.close()
