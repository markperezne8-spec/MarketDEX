import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.runtime_database_migration import migrate_legacy_database_if_needed
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService
from ui.inventory_completed_listing_package_queue_feature import install_inventory_completed_listing_package_queue_feature
from ui.inventory_cost_feature import install_inventory_cost_feature
from ui.inventory_edit_feature import install_inventory_edit_feature
from ui.inventory_listing_execution_history_feature import install_inventory_listing_execution_history_feature
from ui.inventory_listing_execution_readiness_feature import install_inventory_listing_execution_readiness_feature
from ui.inventory_listing_plan_queue_feature import install_inventory_listing_plan_queue_feature
from ui.inventory_listing_workspace_feature import install_inventory_listing_workspace_feature
from ui.inventory_marketplace_listing_package_review_feature import install_inventory_marketplace_listing_package_review_feature
from ui.inventory_marketplace_listing_preparation_feature import install_inventory_marketplace_listing_preparation_feature
from ui.inventory_price_guidance_feature import install_inventory_price_guidance_feature
from ui.inventory_profit_feature import install_inventory_profit_feature
from ui.inventory_sale_completion_feature import install_inventory_sale_completion_feature
from ui.inventory_sale_readiness_feature import install_inventory_sale_readiness_feature
from ui.main_window import MainWindow
from ui.viewport_fit_feature import install_viewport_fit_feature
from ui.wheel_safe_value_controls_feature import install_wheel_safe_value_controls_feature

APP_NAME = 'MarketDEX'
DATABASE_FILENAME = 'marketdex.sqlite3'


def source_root() -> Path:
    return Path(__file__).resolve().parent


def application_data_dir() -> Path:
    override = os.environ.get('MARKETDEX_DATA_DIR')
    if override:
        return Path(override).expanduser().resolve()
    if getattr(sys, 'frozen', False):
        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            return Path(local_app_data) / APP_NAME
        return Path.home() / 'AppData' / 'Local' / APP_NAME
    return source_root() / 'runtime'


def runtime_database_path() -> Path:
    runtime_dir = application_data_dir()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir / DATABASE_FILENAME


def build_main_window(database_path: Path) -> MainWindow:
    mission_control = MissionControlService(database_path)
    inventory = InventoryAppService(database_path)
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
    install_wheel_safe_value_controls_feature(window)
    return window


def initialize_runtime() -> Path:
    database_path = runtime_database_path()
    migrate_legacy_database_if_needed(database_path, source_root())
    MissionControlService(database_path)
    InventoryAppService(database_path)
    return database_path


def main(argv=None) -> int:
    arguments = list(sys.argv if argv is None else argv)
    database_path = runtime_database_path()
    migrate_legacy_database_if_needed(database_path, source_root())
    if '--verify-runtime' in arguments:
        MissionControlService(database_path).snapshot()
        InventoryAppService(database_path).list_inventory()
        print(f'MarketDEX runtime verified: {database_path}')
        return 0
    app = QApplication(arguments)
    window = build_main_window(database_path)
    window.showMaximized()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
