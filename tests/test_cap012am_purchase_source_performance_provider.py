from datetime import date, datetime, timedelta, timezone
from inspect import getsource

import pytest

from core.sale_completion import (
    SaleCompletionAvailable,
    SaleCompletionCompleteness,
    SaleCompletionConflict,
    SaleCompletionCoverage,
    SaleCompletionEvidence,
    SaleCompletionLifecycleState,
    SaleCompletionUnavailable,
)
from core.sale_completion_repository import (
    SaleCompletionRepositoryDiagnostic,
    SaleCompletionRepositoryRead,
)
from core.sale_completion_validation import (
    SaleCompletionEvidenceConflict,
    SaleCompletionEvidenceConflictCode,
)
from reports import purchase_source_performance_provider as provider_module
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from reports.purchase_source_performance_provider import (
    INVENTORY_AVAILABLE,
    PurchaseSourcePerformanceInventoryRead,
    PurchaseSourcePerformanceInventoryRecord,
    PurchaseSourcePerformanceProvider,
)


UTC = timezone.utc
PERIOD_START = date(2026, 1, 1)
PERIOD_END = date(2026, 2, 1)
AS_OF = date(2026, 2, 1)
EXPECTED_AS_OF = datetime(2026, 2, 1, 23, 59, 59, 999999, tzinfo=UTC)
EXPECTED_FROM = datetime(2026, 1, 1, tzinfo=UTC)
EXPECTED_UNTIL = datetime(2026, 2, 1, tzinfo=UTC)


def request() -> PurchaseSourcePerformanceRequest:
    return PurchaseSourcePerformanceRequest(
        PERIOD_START, PERIOD_END, AS_OF, ('inventory', 'listing', 'audit')
    )


def inventory(*records: PurchaseSourcePerformanceInventoryRecord) -> PurchaseSourcePerformanceInventoryRead:
    return PurchaseSourcePerformanceInventoryRead(INVENTORY_AVAILABLE, tuple(records))


def record(inventory_id: str, units: int, source: str) -> PurchaseSourcePerformanceInventoryRecord:
    return PurchaseSourcePerformanceInventoryRecord(inventory_id, units, date(2026, 1, 2), source)


class InventoryReader:
    def __init__(self, read):
        self.read = read
        self.requests = []

    def read_purchase_source_performance_inventory(self, read_request):
        self.requests.append(read_request)
        return self.read


class SaleQuery:
    def __init__(self, read):
        self.read = read
        self.calls = []

    def query(self, **kwargs):
        self.calls.append(kwargs)
        return self.read


def sale_evidence(
    evidence_id: str,
    inventory_id: str,
    *,
    sale_id: str = 'sale-1',
    state: SaleCompletionLifecycleState = SaleCompletionLifecycleState.COMPLETED,
    parent: str | None = None,
    recorded_at: datetime = datetime(2026, 1, 4, tzinfo=UTC),
) -> SaleCompletionEvidence:
    completed = state is SaleCompletionLifecycleState.COMPLETED
    return SaleCompletionEvidence(
        sale_completion_evidence_id=evidence_id,
        sale_id=sale_id,
        inventory_id=inventory_id,
        lifecycle_state=state,
        source_system='canonical-sales',
        recorded_at=recorded_at,
        lineage_parent_evidence_id=parent,
        completed_unit_quantity=1 if completed else None,
        completed_at=recorded_at if completed else None,
    )


def coverage(inventory_ids, *, as_of=EXPECTED_AS_OF, completed_from=EXPECTED_FROM, completed_until=EXPECTED_UNTIL):
    return SaleCompletionCoverage(
        requested_inventory_ids=tuple(inventory_ids),
        requested_sale_ids=(),
        source_systems=('canonical-sales',),
        as_of=as_of,
        evidence_count=0,
        completeness=SaleCompletionCompleteness.COMPLETE,
        completed_from=completed_from,
        completed_until=completed_until,
    )


def available(inventory_ids, evidence=(), **coverage_overrides):
    evidence = tuple(evidence)
    cov = coverage(inventory_ids, **coverage_overrides)
    cov = SaleCompletionCoverage(
        requested_inventory_ids=cov.requested_inventory_ids,
        requested_sale_ids=cov.requested_sale_ids,
        source_systems=cov.source_systems,
        as_of=cov.as_of,
        evidence_count=len(evidence),
        completeness=cov.completeness,
        completed_from=cov.completed_from,
        completed_until=cov.completed_until,
    )
    return SaleCompletionRepositoryRead(SaleCompletionAvailable('available', evidence, cov))


def unavailable(inventory_ids, *, diagnostic=None):
    cov = SaleCompletionCoverage(
        requested_inventory_ids=tuple(inventory_ids),
        requested_sale_ids=(),
        source_systems=('canonical-sales',),
        as_of=EXPECTED_AS_OF,
        evidence_count=0,
        completeness=SaleCompletionCompleteness.UNAVAILABLE,
    )
    return SaleCompletionRepositoryRead(
        SaleCompletionUnavailable('unavailable', 'canonical_sales_unavailable', cov), diagnostic
    )


def conflicting(inventory_ids, diagnostic=None):
    cov = SaleCompletionCoverage(
        requested_inventory_ids=tuple(inventory_ids),
        requested_sale_ids=(),
        source_systems=('canonical-sales',),
        as_of=EXPECTED_AS_OF,
        evidence_count=0,
        completeness=SaleCompletionCompleteness.CONFLICTING,
    )
    return SaleCompletionRepositoryRead(
        SaleCompletionConflict('conflict', 'canonical_sales_conflict', cov), diagnostic
    )


def provider(read, sale_read):
    return PurchaseSourcePerformanceProvider(InventoryReader(read), SaleQuery(sale_read))


def test_valid_multi_source_aggregation_exact_label_separation_and_ordering():
    inventory_read = inventory(
        record('i-2', 3, ' Walmart '),
        record('i-1', 2, 'walmart'),
        record('i-3', 4, 'Target'),
    )
    sales = (
        sale_evidence('e-1', 'i-1'),
        sale_evidence('e-2', 'i-3', sale_id='sale-2', recorded_at=datetime(2026, 1, 5, tzinfo=UTC)),
    )
    response = provider(inventory_read, available(('i-1', 'i-2', 'i-3'), sales)).get_purchase_source_performance_evidence(request())

    assert response.request == request()
    assert [(item.purchase_source_label, item.acquired_units, item.completed_sale_units) for item in response.evidence] == [
        ('Target', 4, 1), ('Walmart', 3, 0), ('walmart', 2, 1)
    ]


def test_zero_qualifying_sales_and_empty_complete_acquisitions_are_valid():
    zero = provider(inventory(record('i-1', 3, 'Target')), available(('i-1',), ())).get_purchase_source_performance_evidence(request())
    assert zero.evidence[0].completed_sale_units == 0

    empty = provider(PurchaseSourcePerformanceInventoryRead(INVENTORY_AVAILABLE), None).get_purchase_source_performance_evidence(request())
    assert empty.evidence == ()


@pytest.mark.parametrize('inventory_state, expected', [('unavailable', 'unavailable'), ('conflicting', 'conflicting')])
def test_inventory_unavailable_and_conflict_fail_closed(inventory_state, expected):
    response = provider(PurchaseSourcePerformanceInventoryRead(inventory_state, reason='inventory reason'), None).get_purchase_source_performance_evidence(request())
    assert response.evidence[0].evidence_state == expected
    assert response.evidence[0].reason == 'inventory reason'
    assert response.evidence[0].acquired_units is None


def test_sale_unavailable_and_conflict_preserve_reason_codes_and_diagnostics():
    conflict = SaleCompletionEvidenceConflict(SaleCompletionEvidenceConflictCode.TIMESTAMP_CONFLICT, ('e-1', 'e-2'))
    diagnostic = SaleCompletionRepositoryDiagnostic((conflict,))
    for read, expected_state, reason_code in (
        (unavailable(('i-1',)), 'unavailable', 'canonical_sales_unavailable'),
        (conflicting(('i-1',), diagnostic), 'conflicting', 'canonical_sales_conflict'),
    ):
        response = provider(inventory(record('i-1', 1, 'Target')), read).get_purchase_source_performance_evidence(request())
        assert response.evidence[0].evidence_state == expected_state
        assert reason_code in response.evidence[0].reason
        assert 'diagnostic_evidence_ids' in response.evidence[0].reason or expected_state == 'unavailable'


@pytest.mark.parametrize('terminal_state', [
    SaleCompletionLifecycleState.REFUNDED,
    SaleCompletionLifecycleState.REVERSED,
    SaleCompletionLifecycleState.SUPERSEDED,
])
def test_terminal_refund_reversal_or_supersession_removes_completed_parent_from_units(terminal_state):
    parent = sale_evidence('completed', 'i-1')
    child = sale_evidence('terminal', 'i-1', state=terminal_state, parent='completed', recorded_at=datetime(2026, 1, 5, tzinfo=UTC))
    response = provider(inventory(record('i-1', 1, 'Target')), available(('i-1',), (parent, child))).get_purchase_source_performance_evidence(request())
    assert response.evidence[0].completed_sale_units == 0


def test_period_as_of_translation_and_inventory_request_are_explicit_and_immutable():
    reader = InventoryReader(inventory(record('i-1', 1, 'Target')))
    query = SaleQuery(available(('i-1',), ()))
    original = request()
    PurchaseSourcePerformanceProvider(reader, query).get_purchase_source_performance_evidence(original)
    assert reader.requests[0].period_start == PERIOD_START
    assert reader.requests[0].period_end == PERIOD_END
    assert reader.requests[0].as_of == AS_OF
    assert query.calls[0] == {
        'inventory_ids': ('i-1',), 'as_of': EXPECTED_AS_OF,
        'completed_from': EXPECTED_FROM, 'completed_until': EXPECTED_UNTIL,
    }
    assert original == request()
    with pytest.raises(Exception):
        reader.requests[0].period_start = date(2026, 1, 2)


@pytest.mark.parametrize('override', [
    {'as_of': EXPECTED_AS_OF - timedelta(seconds=1)},
    {'completed_from': EXPECTED_FROM + timedelta(seconds=1)},
    {'completed_until': EXPECTED_UNTIL + timedelta(seconds=1)},
])
def test_sale_coverage_mismatch_fails_closed(override):
    read = available(('i-1',), (), **override)
    response = provider(inventory(record('i-1', 1, 'Target')), read).get_purchase_source_performance_evidence(request())
    assert response.evidence[0].evidence_state == 'conflicting'


@pytest.mark.parametrize('malformed', [object(), type('MalformedRead', (), {'result': object()})()])
def test_malformed_sale_responses_fail_closed_without_optional_attribute_assumptions(malformed):
    response = provider(inventory(record('i-1', 1, 'Target')), malformed).get_purchase_source_performance_evidence(request())
    assert response.evidence[0].evidence_state == 'unavailable'


def test_provider_has_no_concrete_sqlite_dependency_and_never_mutates_sources():
    source = getsource(provider_module)
    assert 'sqlite' not in source.lower()
    inventory_read = inventory(record('i-1', 1, 'Target'))
    response = provider(inventory_read, available(('i-1',), ())).get_purchase_source_performance_evidence(request())
    assert inventory_read.records[0].purchase_source_label == 'Target'
    assert response.provenance == (
        'purchase-source-performance-provider:purchase-source-performance|purchase-source-sell-through-units-v1|2026-01-01|2026-02-01|2026-02-01|business_inventory|purchase_source|audit,inventory,listing:inventory',
        'purchase-source-performance-provider:purchase-source-performance|purchase-source-sell-through-units-v1|2026-01-01|2026-02-01|2026-02-01|business_inventory|purchase_source|audit,inventory,listing:sale_completion',
    )
