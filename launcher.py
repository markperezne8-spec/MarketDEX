import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from core.runtime_database_migration import migrate_legacy_database_if_needed
from services.mission_control_service import MissionControlService
from services.inventory_app_service import InventoryAppService
from ui.main_window import MainWindow
from ui.inventory_edit_feature import install_inventory_edit_feature
from ui.inventory_cost_feature import install_inventory_cost_feature
from ui.inventory_sale_readiness_feature import install_inventory_sale_readiness_feature
from ui.inventory_profit_feature import install_inventory_profit_feature
from ui.inventory_price_guidance_feature import install_inventory_price_guidance_feature
from ui.inventory_listing_workspace_feature import install_inventory_listing_workspace_feature
from ui.inventory_listing_plan_queue_feature import install_inventory_listing_plan_queue_feature
from ui.inventory_listing_execution_readiness_feature import install_inventory_listing_execution_readiness_feature
from ui.inventory_marketplace_listing_preparation_feature import install_inventory_marketplace_listing_preparation_feature
from ui.inventory_marketplace_listing_package_review_feature import install_inventory_marketplace_listing_package_review_feature
from ui.inventory_completed_listing_package_queue_feature import install_inventory_completed_listing_package_queue_feature
from ui.inventory_listing_execution_history_feature import install_inventory_listing_execution_history_feature
from ui.inventory_sale_completion_feature import install_inventory_sale_completion_feature
from ui.viewport_fit_feature import install_viewport_fit_feature


def runtime_database_path():
    runtime_dir = Path(__file__).parent / 'runtime'
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir / 'marketdex.sqlite3'


def desktop_launch_size(available):
    width = min(1320, max(960, int(available.width() * 0.86)))
    height = min(760, max(640, int(available.height() * 0.82)))
    return width, height


if __name__ == '__main__':
    database_path = runtime_database_path()
    migrate_legacy_database_if_needed(database_path, Path(__file__).parent)
    mission_control = MissionControlService(database_path)
    inventory = InventoryAppService(database_path)
    app = QApplication(sys.argv)
    window = MainWindow(mission_control, inventory)
    install_inventory_edit_feature(window)
    install_inventory_cost_feature(window)
    install_inventory_sale_readiness_feature(window)
    install_inventory_profit_feature(window)
    install_inventory_price_guidance_feature(window)
    install_inventory_listing_workspace_feature(window)
    install_inventory_listing_plan_queue_feature(window)
    install_inventory_listing_execution_readiness_feature(window)
    install_inventory_marketplace_listing_preparation_feature(window)
    install_inventory_marketplace_listing_package_review_feature(window)
    install_inventory_completed_listing_package_queue_feature(window)
    install_inventory_listing_execution_history_feature(window)
    install_inventory_sale_completion_feature(window)
    install_viewport_fit_feature(window)
    available = app.primaryScreen().availableGeometry()
    width, height = desktop_launch_size(available)
    window.resize(width, height)
    window.show()
    sys.exit(app.exec())
