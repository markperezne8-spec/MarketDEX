from dataclasses import dataclass
from pathlib import Path

from composition.feature_catalog import install_features
from market_intelligence.composition import MarketIntelligenceComposition
from reports.definitions import ReportCatalog, build_report_catalog
from reports.inventory_age_provider import ApplicationInventoryAgeInputProvider
from reports.inventory_age_query import InventoryAgeReportQueryService
from services.collection_position_service import CollectionPositionService
from services.inventory_app_service import InventoryAppService
from services.inventory_detail_read import InventoryDetailReadAdapter
from services.inventory_product_link_read import InventoryProductLinkReadAdapter
from services.mission_control_service import MissionControlService
from services.product_registry_lookup_service import ProductRegistryLookupService
from ui.main_window import MainWindow
from ui.product_registry_workspace import ProductRegistryWorkspace
from ui.collection_position_workspace import CollectionPositionWorkspace
from ui.market_intelligence_workspace import MarketIntelligenceWorkspace
from ui.shell_workspace_catalog import (
    register_collection_position_workspace,
    register_market_intelligence_workspace,
    register_product_registry_workspace,
)
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
        self.inventory_age_input_provider = ApplicationInventoryAgeInputProvider(
            InventoryDetailReadAdapter(self.inventory.database.read_connection),
            InventoryProductLinkReadAdapter(self.inventory.database.read_connection),
        )
        self.inventory_age_report_query = InventoryAgeReportQueryService(
            self.inventory_age_input_provider
        )
        self.product_registry_lookup = ProductRegistryLookupService(self.database_path)
        self.collection_positions = CollectionPositionService(self.database_path)
        self.workspace_registry = WorkspaceRegistry()
        self.market_intelligence = MarketIntelligenceComposition()
        self.report_catalog: ReportCatalog = build_report_catalog()

    def build_main_window(self) -> MainWindow:
        window = MainWindow(self.mission_control, self.inventory)
        install_features(window)
        product_registry_workspace = ProductRegistryWorkspace(
            self.product_registry_lookup,
            window,
        )
        register_product_registry_workspace(
            self.workspace_registry,
            product_registry_workspace,
        )
        collection_position_workspace = CollectionPositionWorkspace(
            self.collection_positions,
            window,
        )
        register_collection_position_workspace(
            self.workspace_registry,
            collection_position_workspace,
        )
        market_intelligence_workspace = MarketIntelligenceWorkspace(
            self.market_intelligence,
            window,
        )
        register_market_intelligence_workspace(
            self.workspace_registry,
            market_intelligence_workspace,
        )
        install_viewport_fit_feature(window, self.workspace_registry)
        window.product_registry_workspace = product_registry_workspace
        window.collection_position_workspace = collection_position_workspace
        window.market_intelligence_workspace = market_intelligence_workspace
        window.application_composition = self
        window.market_intelligence = self.market_intelligence
        return window

    def verify_runtime(self) -> None:
        self.mission_control.snapshot()
        self.inventory.list_inventory()
        self.product_registry_lookup.search('runtime-verification')
        self.collection_positions.list_positions()
