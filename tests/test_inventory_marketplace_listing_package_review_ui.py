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
from ui.inventory_listing_execution_readiness_feature import install_inventory_listing_execution_readiness_feature
from ui.inventory_marketplace_listing_preparation_feature import install_inventory_marketplace_listing_preparation_feature
from ui.inventory_marketplace_listing_package_review_feature import install_inventory_marketplace_listing_package_review_feature, listing_package_review_decision


def test_review_decision_requires_prepared_package():
    row = {'asset_id': 'asset-1', 'asset_name': 'Test ETB', 'asset_type': 'SEALED', 'quantity': 1, 'total_cost_minor': 10000}
    plan = {'marketplace': 'eBay', 'target_sale_price_minor': 15750}
    assert listing_package_review_decision(row, plan)['reviewable'] is True
    plan['marketplace'] = ''
    assert listing_package_review_decision(row, plan)['reviewable'] is False


def test_operator_can_approve_or_return_reviewable_package(tmp_path):
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
    install_inventory_marketplace_listing_preparation_feature(window)
    install_inventory_marketplace_listing_package_review_feature(window)
    window.inventory_table.selectRow(0)
    window.inventory_target_sale_price.setValue(157.50)
    window.inventory_save_listing_plan.click()
    assert 'READY FOR OPERATOR REVIEW' in window.inventory_marketplace_listing_package_review_summary.text()
    window.inventory_approve_listing_package.click()
    assert 'PACKAGE APPROVED' in window.inventory_marketplace_listing_package_review_status.text()
    window.inventory_return_listing_package.click()
    assert 'RETURNED FOR CHANGES' in window.inventory_marketplace_listing_package_review_status.text()
    window.close()
