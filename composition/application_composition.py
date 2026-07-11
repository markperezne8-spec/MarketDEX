from dataclasses import dataclass
from pathlib import Path

from composition.feature_catalog import install_features
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService
from ui.main_window import MainWindow
from ui.viewport_fit_feature import install_viewport_fit_feature
from ui.workspace_registry import WorkspaceRegistry


@dataclass
class ApplicationComposition:
    """Builds one coherent MarketDEX runtime from canonical dependencies."""

    database_path: Path

    def __post_init__(self) -> None:
        self.database_path = Path(self.database_path)
        self.mission_control = MissionControlService(self.database_path)
        self.inventory = InventoryAppService(self.database_path)
        self.workspace_registry = WorkspaceRegistry()

    def build_main_window(self) -> MainWindow:
        window = MainWindow(self.mission_control, self.inventory)
        install_features(window)
        install_viewport_fit_feature(window, self.workspace_registry)
        window.application_composition = self
        return window

    def verify_runtime(self) -> None:
        self.mission_control.snapshot()
        self.inventory.list_inventory()
