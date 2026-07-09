import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from core.database_manager import DatabaseManager
from core.listing_package_review_repository import ListingPackageReviewRepository
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
from ui.inventory_marketplace_listing_package_review_feature import install_inventory_marketplace_listing_package_review_feature
from ui.inventory_completed_listing_package_queue_feature import install_inventory_completed_listing_package_queue_feature


def install_chain(window):
    install_inventory_sale_readiness_feature(window)
    install_inventory_profit_feature(window)
    install_inventory_price_guidance_feature(window)
    install_inventory_listing_workspace_feature(window)
    install_inventory_listing_plan_queue_feature(window)
    install_inventory_listing_execution_readiness_feature(window)
    install_inventory_marketplace_listing_preparation_feature(window)
    install_inventory_marketplace_listing_package_review_feature(window)
    install_inventory_completed_listing_package_queue_feature(window)


def test_repository_lists_only_completed_reviews(tmp_path):
    database = DatabaseManager(tmp_path / 'marketdex.sqlite3')
    database.initialize()
    repository = ListingPackageReviewRepository(database)
    repository.save('approved', 'PACKAGE APPROVED • OFFLINE ONLY')
    repository.save('returned', 'RETURNED FOR CHANGES')
    assert [row['asset_id'] for row in repository.list_completed()] == ['approved']


def test_approved_package_enters_queue_and_return_removes_it(tmp_path):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / 'marketdex.sqlite3'
    inventory = InventoryAppService(path)
    inventory.add_asset(asset_id='asset-1', asset_name='Test ETB', asset_type='SEALED', quantity=1, total_cost_minor=10000, request_id='add-1')
    window = MainWindow(MissionControlService(path), inventory)
    install_chain(window)
    window.inventory_table.selectRow(0)
    window.inventory_marketplace.setCurrentText('EBAY')
    window.inventory_target_sale_price.setValue(157.50)
    window.inventory_save_listing_plan.click()
    window.inventory_approve_listing_package.click()
    assert window.inventory_completed_listing_package_queue_table.rowCount() == 1
    assert window.inventory_completed_listing_package_queue_table.item(0, 0).text() == 'Test ETB'
    assert window.inventory_completed_listing_package_queue_table.item(0, 3).text() == 'READY FOR OPERATOR HANDOFF'
    window.inventory_return_listing_package.click()
    assert window.inventory_completed_listing_package_queue_table.rowCount() == 0
    window.close()
