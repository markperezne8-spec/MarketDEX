from dataclasses import dataclass
from datetime import date
from pathlib import Path

from composition.feature_catalog import install_features
from core.sale_completion_repository_registration import register_sale_completion_repository
from core.sqlite_inventory_acquisition_projection_repository import SqliteInventoryAcquisitionProjectionRepository
from market_intelligence.composition import MarketIntelligenceComposition
from reports.definitions import ReportCatalog, ReportDefinition, build_report_catalog
from reports.inventory_age_provider import ApplicationInventoryAgeInputProvider
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest
from reports.inventory_age_query import (
    InventoryAgeReportQueryResult,
    InventoryAgeReportQueryService,
)
from reports.inventory_turnover_presentation import present_inventory_turnover
from reports.inventory_turnover_preview import build_inventory_turnover_preview_result
from reports.report_query_request import ReportQueryRequest
from reports.report_query_service import ReportQueryService
from reports.purchase_source_performance_inventory_adapter import PurchaseSourcePerformanceInventoryAdapter
from reports.purchase_source_performance_provider import PurchaseSourcePerformanceProvider
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from reports.purchase_source_performance_presentation import present_purchase_source_performance
from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryService
from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryResponse
from services.collection_position_service import CollectionPositionService
from services.inventory_app_service import InventoryAppService
from services.market_pricing_service import MarketPricingService, TCGplayerMarketPriceProvider
from services.inventory_detail_read import InventoryDetailReadAdapter
from services.inventory_product_link_read import InventoryProductLinkReadAdapter
from services.mission_control_service import MissionControlService
from services.product_registry_lookup_service import ProductRegistryLookupService
from services.sale_completion_query_service import SaleCompletionQueryService
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
from ui.data_freshness_feature import install_data_freshness_feature
from ui.inventory_workspace_focus_feature import (
    install_inventory_workspace_focus_feature,
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
        self.market_pricing = MarketPricingService(self.inventory, TCGplayerMarketPriceProvider())
        self.sale_completion_repository = register_sale_completion_repository(self.inventory.database)
        self.sale_completion_query = SaleCompletionQueryService(self.sale_completion_repository)
        self.inventory_acquisition_projection_repository = SqliteInventoryAcquisitionProjectionRepository(
            self.inventory.database
        )
        self.purchase_source_performance_inventory_adapter = PurchaseSourcePerformanceInventoryAdapter(
            self.inventory_acquisition_projection_repository
        )
        self.purchase_source_performance_provider = PurchaseSourcePerformanceProvider(
            self.purchase_source_performance_inventory_adapter,
            self.sale_completion_query,
        )
        self.purchase_source_performance_query = PurchaseSourcePerformanceQueryService(
            self.purchase_source_performance_provider
        )
        self.purchase_source_performance_presentation = self._build_purchase_source_performance_presentation()
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
            self.purchase_source_performance_query,
        )
        self.inventory_turnover_preview_result = (
            build_inventory_turnover_preview_result()
        )
        self.inventory_turnover_presentation = present_inventory_turnover(
            self.inventory_turnover_preview_result
        )

    def _build_purchase_source_performance_presentation(self):
        """Build one deterministic, composition-owned read-only snapshot for Reports."""
        request = PurchaseSourcePerformanceRequest(
            period_start=date(2026, 1, 1),
            period_end=date(2026, 2, 1),
            as_of=date(2026, 2, 1),
            source_coverage_required=("inventory", "sale_completion"),
        )
        response = self.purchase_source_performance_query.get_evidence_for_request(request)
        return present_purchase_source_performance(response)

    def list_reports(self) -> tuple[ReportDefinition, ...]:
        """Return the immutable, composition-owned report catalog view."""
        return self.report_catalog.list_definitions()

    def get_report_definition(self, report_id: str) -> ReportDefinition:
        """Resolve one immutable report definition through the composition boundary."""
        return self.report_catalog.get(report_id)

    def report_evidence_families(self, report_id: str) -> tuple[str, ...]:
        """Return canonical evidence families for one approved report."""
        return self.get_report_definition(report_id).evidence_families

    def report_source_domains(self, report_id: str) -> tuple[str, ...]:
        """Return canonical source domains for one approved report."""
        return self.get_report_definition(report_id).source_domains

    def report_description(self, report_id: str) -> str:
        """Return the canonical description for one approved report."""
        return self.get_report_definition(report_id).description

    def report_execution_mode(self, report_id: str) -> str:
        """Return the validated execution mode for one approved report."""
        return self.get_report_definition(report_id).execution_mode

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

    def query_purchase_source_performance(
        self,
        request: PurchaseSourcePerformanceRequest,
    ) -> PurchaseSourcePerformanceQueryResponse:
        """Query Purchase Source Performance through the canonical Reports boundary."""
        if not isinstance(request, PurchaseSourcePerformanceRequest):
            raise TypeError(
                'Purchase Source Performance query requires PurchaseSourcePerformanceRequest'
            )
        report_request = ReportQueryRequest(
            'purchase-source-performance',
            purchase_source_request=request,
        )
        return self.report_query.query(report_request)

    def build_main_window(self) -> MainWindow:
        window = MainWindow(self.mission_control, self.inventory, market_pricing_service=self.market_pricing)
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
        reports_workspace = ReportsWorkspace(
            self.report_catalog,
            self.query_report,
            window,
            turnover_presentation=self.inventory_turnover_presentation,
            purchase_source_presentation=self.purchase_source_performance_presentation,
            purchase_source_query=self.query_purchase_source_performance,
        )
        register_reports_workspace(
            self.workspace_registry,
            reports_workspace,
        )
        install_viewport_fit_feature(window, self.workspace_registry)
        install_data_freshness_feature(window)
        install_inventory_workspace_focus_feature(window)
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
