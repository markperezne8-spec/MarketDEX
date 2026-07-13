from dataclasses import dataclass
from datetime import date
from pathlib import Path

from composition.feature_catalog import install_features
from market_intelligence.composition import MarketIntelligenceComposition
from reports.definitions import ReportCatalog, ReportDefinition, build_report_catalog
from reports.inventory_age_provider import ApplicationInventoryAgeInputProvider
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest
from reports.inventory_age_query import (
    InventoryAgeReportQueryResult,
    InventoryAgeReportQueryService,
)
from reports.report_query_request import ReportQueryRequest
from reports.report_query_service import ReportQueryService
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
from ui.reports_workspace import ReportsWorkspace
from ui.shell_workspace_catalog import (
    register_collection_position_workspace,
    register_market_intelligence_workspace,
    register_product_registry_workspace,
    register_reports_workspace,
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
        self.report_query = ReportQueryService(
            self.report_catalog,
            self.inventory_age_report_query,
        )

    def list_reports(self) -> tuple[ReportDefinition, ...]:
        """Return the immutable, composition-owned report catalog view."""
        return self.report_catalog.list_definitions()

    def get_report_definition(self, report_id: str) -> ReportDefinition:
        """Resolve one immutable report definition through the composition boundary."""
        return self.report_catalog.get(report_id)

    def query_inventory_age(
        self,
        inventory_position_id: str,
        as_of_date: date,
    ) -> InventoryAgeReportQueryResult:
        """Query Inventory Age through the composition-owned report service."""
        request = InventoryAgeReportQueryRequest(inventory_position_id, as_of_date)
        return self.inventory_age_report_query.get_inventory_age_for_request(request)

    def query_report(
        self,
        report_id: str,
        inventory_position_id: str,
        as_of_date: date,
    ) -> InventoryAgeReportQueryResult:
        """Route a catalog-approved report through the Reports query service."""
        request = ReportQueryRequest(
            report_id,
            InventoryAgeReportQueryRequest(inventory_position_id, as_of_date),
        )
        return self.report_query.query(
            request,
            query_inventory_age=self.query_inventory_age,
        )

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
        reports_workspace = ReportsWorkspace(self.report_catalog, window)
        register_reports_workspace(
            self.workspace_registry,
            reports_workspace,
        )
        install_viewport_fit_feature(window, self.workspace_registry)
        window.product_registry_workspace = product_registry_workspace
        window.collection_position_workspace = collection_position_workspace
        window.market_intelligence_workspace = market_intelligence_workspace
        window.reports_workspace = reports_workspace
        window.application_composition = self
        window.market_intelligence = self.market_intelligence
        return window

    def verify_runtime(self) -> None:
        self.mission_control.snapshot()
        self.inventory.list_inventory()
        self.product_registry_lookup.search('runtime-verification')
        self.collection_positions.list_positions()
