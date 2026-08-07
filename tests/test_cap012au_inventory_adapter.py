from datetime import date, datetime, timezone

from core.inventory_acquisition_projection import (
    InventoryAcquisitionProjectionAvailable,
    InventoryAcquisitionProjectionConflict,
    InventoryAcquisitionProjectionCoverage,
    InventoryAcquisitionProjectionDiagnostic,
    InventoryAcquisitionProjectionRecord,
    InventoryAcquisitionProjectionRequest,
    InventoryAcquisitionProjectionUnavailable,
)
from reports.purchase_source_performance_inventory_adapter import PurchaseSourcePerformanceInventoryAdapter
from reports.purchase_source_performance_provider import PurchaseSourcePerformanceInventoryReadRequest


class FakeProjectionRepository:
    def __init__(self, result):
        self.result = result
        self.requests = []

    def read_inventory_acquisition_projection(self, request):
        self.requests.append(request)
        return self.result


def _request():
    return PurchaseSourcePerformanceInventoryReadRequest(date(2026, 7, 1), date(2026, 8, 1), date(2026, 7, 31))


def _available(request):
    projection_request = InventoryAcquisitionProjectionRequest(
        request.period_start, request.period_end,
        datetime(2026, 7, 31, 23, 59, 59, 999999, tzinfo=timezone.utc),
    )
    return InventoryAcquisitionProjectionAvailable(
        projection_request,
        InventoryAcquisitionProjectionCoverage(request.period_start, request.period_end, projection_request.as_of),
        (InventoryAcquisitionProjectionRecord('INV-1', 2, date(2026, 7, 3), '  Dealer  '),),
        ('sqlite.inventory_acquisition_evidence:EV-1',),
    )


def test_maps_canonical_projection_and_exact_utc_boundary():
    request = _request()
    repo = FakeProjectionRepository(_available(request))
    result = PurchaseSourcePerformanceInventoryAdapter(repo).read_purchase_source_performance_inventory(request)
    assert result.outcome == 'available'
    assert result.records[0].inventory_id == 'INV-1'
    assert result.records[0].purchase_source_label == 'Dealer'
    assert repo.requests[0].as_of == datetime(2026, 7, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)


def test_maps_empty_available_without_inventing_records():
    request = _request()
    pr = InventoryAcquisitionProjectionRequest(request.period_start, request.period_end, datetime(2026, 7, 31, 23, 59, 59, 999999, tzinfo=timezone.utc))
    result = InventoryAcquisitionProjectionAvailable(pr, InventoryAcquisitionProjectionCoverage(request.period_start, request.period_end, pr.as_of), (), ('sqlite.inventory_acquisition_evidence:empty',))
    assert PurchaseSourcePerformanceInventoryAdapter(FakeProjectionRepository(result)).read_purchase_source_performance_inventory(request).records == ()


def test_preserves_unavailable_and_conflicting_fail_closed_states():
    request = _request()
    pr = InventoryAcquisitionProjectionRequest(request.period_start, request.period_end, datetime(2026, 7, 31, 23, 59, 59, 999999, tzinfo=timezone.utc))
    for source, expected in ((InventoryAcquisitionProjectionUnavailable(pr, InventoryAcquisitionProjectionDiagnostic('missing_authority', 'missing')), 'unavailable'), (InventoryAcquisitionProjectionConflict(pr, InventoryAcquisitionProjectionDiagnostic('duplicate_identity', 'duplicate')), 'conflicting')):
        result = PurchaseSourcePerformanceInventoryAdapter(FakeProjectionRepository(source)).read_purchase_source_performance_inventory(request)
        assert result.outcome == expected
        assert result.records == ()


def test_projection_dependency_failure_is_unavailable():
    class Broken:
        def read_inventory_acquisition_projection(self, request):
            raise RuntimeError('offline')
    result = PurchaseSourcePerformanceInventoryAdapter(Broken()).read_purchase_source_performance_inventory(_request())
    assert result.outcome == 'unavailable'
    assert result.records == ()
