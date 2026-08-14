from datetime import date
import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication

from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from composition.application_composition import ApplicationComposition
from market_intelligence.composition import MarketIntelligenceComposition
from services.inventory_app_service import InventoryAppService
from services.mission_control_service import MissionControlService
from ui.main_window import MainWindow
from ui.workspace_registry import WorkspaceRegistry


def test_application_composition_owns_one_shared_runtime_graph(tmp_path):
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    assert isinstance(composition.mission_control, MissionControlService)
    assert isinstance(composition.inventory, InventoryAppService)
    assert isinstance(composition.workspace_registry, WorkspaceRegistry)
    assert isinstance(composition.market_intelligence, MarketIntelligenceComposition)
    assert composition.database_path == tmp_path / 'marketdex.sqlite3'


def test_application_composition_builds_the_existing_shell_and_preserves_identity(tmp_path):
    app = QApplication.instance() or QApplication([])
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    window = composition.build_main_window()

    assert isinstance(window, MainWindow)
    assert window.application_composition is composition
    assert window.service is composition.mission_control
    assert window.inventory_service is composition.inventory
    assert window.workspace_registry is composition.workspace_registry
    assert window.workspace_host.registry is composition.workspace_registry
    assert window.market_intelligence is composition.market_intelligence
    window.close()


def test_application_composition_verifies_the_runtime_without_creating_a_window(tmp_path):
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    composition.verify_runtime()

    assert composition.database_path.exists()


def test_application_composition_routes_purchase_source_performance_through_reports_boundary(tmp_path):
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')
    request = PurchaseSourcePerformanceRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=__import__('datetime').date(2026, 2, 1),
        source_coverage_required=('inventory', 'sale_completion'),
    )

    response = composition.query_purchase_source_performance(request)

    assert response.request == request
    assert response.source_domains == ('inventory', 'sale_completion')
    assert response.source_coverage
    assert response.provenance
