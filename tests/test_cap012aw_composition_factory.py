from pathlib import Path

from composition.application_composition import ApplicationComposition
from core.inventory_acquisition_projection_repository import InventoryAcquisitionProjectionRepository
from reports.purchase_source_performance_provider import PurchaseSourcePerformanceInventoryReader, PurchaseSourcePerformanceProvider
from core.sale_completion_repository import SaleCompletionRepository


def test_composition_builds_purchase_source_provider_from_shared_database(tmp_path):
    composition = ApplicationComposition(Path(tmp_path) / 'marketdex.sqlite3')

    assert composition.sale_completion_repository is not None
    assert isinstance(composition.sale_completion_repository, SaleCompletionRepository)
    assert isinstance(composition.inventory_acquisition_projection_repository, InventoryAcquisitionProjectionRepository)
    assert isinstance(composition.purchase_source_performance_inventory_adapter, PurchaseSourcePerformanceInventoryReader)
    assert isinstance(composition.purchase_source_performance_provider, PurchaseSourcePerformanceProvider)
    assert composition.sale_completion_repository._database_manager is composition.inventory.database
    assert composition.inventory_acquisition_projection_repository._database_manager is composition.inventory.database


def test_composition_construction_does_not_write_audit_or_evidence(tmp_path):
    path = Path(tmp_path) / 'marketdex.sqlite3'
    before = ApplicationComposition(path).inventory.database
    with before.read_connection() as connection:
        counts_before = tuple(connection.execute(
            "SELECT (SELECT COUNT(*) FROM audit_events), (SELECT COUNT(*) FROM inventory_acquisition_evidence)"
        ).fetchone())
    ApplicationComposition(path)
    with before.read_connection() as connection:
        counts_after = tuple(connection.execute(
            "SELECT (SELECT COUNT(*) FROM audit_events), (SELECT COUNT(*) FROM inventory_acquisition_evidence)"
        ).fetchone())
    assert counts_after == counts_before
