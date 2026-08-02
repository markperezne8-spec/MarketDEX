from datetime import date

from core.sale_completion import SaleCompletionAvailable
from core.sale_completion_repository import SaleCompletionRepositoryRead
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from reports.purchase_source_performance_provider import (
    INVENTORY_AVAILABLE,
    PurchaseSourcePerformanceInventoryRead,
    PurchaseSourcePerformanceInventoryRecord,
    PurchaseSourcePerformanceProvider,
)


def request():
    return PurchaseSourcePerformanceRequest(date(2026, 1, 1), date(2026, 2, 1), date(2026, 2, 1), ('inventory', 'listing', 'audit'))


def inventory(*records):
    return PurchaseSourcePerformanceInventoryRead(INVENTORY_AVAILABLE, tuple(records))


class InventoryReader:
    def __init__(self, read): self.read = read; self.requests = []
    def read_purchase_source_performance_inventory(self, request): self.requests.append(request); return self.read


class SaleQuery:
    def __init__(self, read): self.read = read; self.calls = []
    def query(self, **kwargs): self.calls.append(kwargs); return self.read


def sale_read(evidence=()):
    from core.sale_completion import SaleCompletionCoverage, SaleCompletionCompleteness
    from datetime import datetime, timezone
    coverage = SaleCompletionCoverage(tuple(sorted({item.inventory_id for item in evidence})), (), ('canonical-sales',), datetime(2026, 2, 1, 23, 59, 59, 999999, tzinfo=timezone.utc), len(evidence), SaleCompletionCompleteness.COMPLETE, datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 2, 1, tzinfo=timezone.utc))
    return SaleCompletionRepositoryRead(SaleCompletionAvailable('available', tuple(evidence), coverage))


def test_provider_composes_exact_trim_only_sources_and_preserves_request():
    from core.sale_completion import SaleCompletionEvidence, SaleCompletionLifecycleState
    from datetime import datetime, timezone
    r = request(); a = PurchaseSourcePerformanceInventoryRecord('i-2', 3, date(2026, 1, 2), ' Walmart '); b = PurchaseSourcePerformanceInventoryRecord('i-1', 2, date(2026, 1, 3), 'walmart')
    evidence = (SaleCompletionEvidence('e-1', 's-1', 'i-1', SaleCompletionLifecycleState.COMPLETED, 'canonical-sales', datetime(2026, 1, 4, tzinfo=timezone.utc), completed_unit_quantity=1, completed_at=datetime(2026, 1, 4, tzinfo=timezone.utc)),)
    reader, query = InventoryReader(inventory(a, b)), SaleQuery(sale_read(evidence)); response = PurchaseSourcePerformanceProvider(reader, query).get_purchase_source_performance_evidence(r)
    assert response.request is r
    assert [(item.purchase_source_label, item.acquired_units, item.completed_sale_units) for item in response.evidence] == [('Walmart', 3, 0), ('walmart', 2, 1)]
    assert query.calls[0]['inventory_ids'] == ('i-1', 'i-2')
    assert query.calls[0]['completed_until'].isoformat() == '2026-02-01T00:00:00+00:00'


def test_provider_propagates_unavailable_and_conflict_without_numeric_values():
    r = request(); reader = InventoryReader(PurchaseSourcePerformanceInventoryRead('unavailable', reason='inventory offline'))
    response = PurchaseSourcePerformanceProvider(reader, SaleQuery(None)).get_purchase_source_performance_evidence(r)
    assert response.evidence[0].evidence_state == 'unavailable'; assert response.evidence[0].acquired_units is None


def test_provider_is_fail_closed_for_duplicate_inventory_identity_and_does_not_query_sales():
    record = PurchaseSourcePerformanceInventoryRecord('same', 1, date(2026, 1, 2), 'Target'); reader = InventoryReader(inventory(record, record)); query = SaleQuery(None)
    response = PurchaseSourcePerformanceProvider(reader, query).get_purchase_source_performance_evidence(request())
    assert response.evidence[0].evidence_state == 'conflicting'; assert query.calls == []
