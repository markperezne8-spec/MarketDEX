from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from typing import Protocol, runtime_checkable

from core.sale_completion import (
    SaleCompletionAvailable,
    SaleCompletionConflict,
    SaleCompletionCompleteness,
    SaleCompletionUnavailable,
)
from core.sale_completion_repository import (
    SaleCompletionRepositoryDiagnostic,
    SaleCompletionRepositoryRead,
)
from services.sale_completion_query_service import SaleCompletionQueryService
from reports.purchase_source_performance_calculator import PurchaseSourcePerformanceEvidence
from reports.purchase_source_performance_contract import PurchaseSourcePerformanceRequest
from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryResponse


INVENTORY_AVAILABLE = 'available'
INVENTORY_UNAVAILABLE = 'unavailable'
INVENTORY_CONFLICTING = 'conflicting'
INVENTORY_READ_OUTCOMES = frozenset({INVENTORY_AVAILABLE, INVENTORY_UNAVAILABLE, INVENTORY_CONFLICTING})
UTC = timezone.utc


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformanceInventoryReadRequest:
    period_start: date
    period_end: date
    as_of: date


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformanceInventoryRecord:
    inventory_id: str
    acquired_units: int
    acquisition_date: date
    purchase_source_label: str

    def __post_init__(self) -> None:
        inventory_id = str(self.inventory_id).strip()
        label = str(self.purchase_source_label).strip()
        if not inventory_id or not label:
            raise ValueError('inventory_id and purchase_source_label are required')
        if type(self.acquired_units) is not int or self.acquired_units <= 0:
            raise ValueError('acquired_units must be a positive integer')
        if type(self.acquisition_date) is not date:
            raise TypeError('acquisition_date must be a date')
        object.__setattr__(self, 'inventory_id', inventory_id)
        object.__setattr__(self, 'purchase_source_label', label)


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformanceInventoryRead:
    outcome: str
    records: tuple[PurchaseSourcePerformanceInventoryRecord, ...] = ()
    reason: str = 'complete Inventory acquisition coverage'

    def __post_init__(self) -> None:
        outcome = str(self.outcome).strip().lower()
        if outcome not in INVENTORY_READ_OUTCOMES:
            raise ValueError(f'unsupported Inventory acquisition outcome: {outcome}')
        if not isinstance(self.records, tuple) or any(not isinstance(item, PurchaseSourcePerformanceInventoryRecord) for item in self.records):
            raise TypeError('records must be a tuple of Inventory acquisition records')
        if outcome != INVENTORY_AVAILABLE and self.records:
            raise ValueError('unavailable or conflicting Inventory reads must not expose records')
        if not str(self.reason).strip():
            raise ValueError('reason is required')
        object.__setattr__(self, 'outcome', outcome)
        object.__setattr__(self, 'reason', str(self.reason).strip())


@runtime_checkable
class PurchaseSourcePerformanceInventoryReader(Protocol):
    def read_purchase_source_performance_inventory(
        self, request: PurchaseSourcePerformanceInventoryReadRequest,
    ) -> PurchaseSourcePerformanceInventoryRead: ...


def _at_utc_start(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=UTC)


def _at_utc_end(value: date) -> datetime:
    return datetime.combine(value, time.max, tzinfo=UTC)


class PurchaseSourcePerformanceProvider:
    """Constructor-injected, read-only orchestration for one report request."""

    def __init__(
        self,
        inventory_reader: PurchaseSourcePerformanceInventoryReader,
        sale_completion_query: SaleCompletionQueryService,
    ) -> None:
        self._inventory_reader = inventory_reader
        self._sale_completion_query = sale_completion_query

    def get_purchase_source_performance_evidence(
        self, request: PurchaseSourcePerformanceRequest,
    ) -> PurchaseSourcePerformanceQueryResponse:
        if not isinstance(request, PurchaseSourcePerformanceRequest):
            raise TypeError('request must be a PurchaseSourcePerformanceRequest')

        inventory_request = PurchaseSourcePerformanceInventoryReadRequest(
            request.period_start, request.period_end, request.as_of,
        )
        try:
            inventory_read = self._inventory_reader.read_purchase_source_performance_inventory(inventory_request)
        except Exception:
            return self._status_response(request, 'unavailable', 'Inventory acquisition read dependency unavailable')
        if not isinstance(inventory_read, PurchaseSourcePerformanceInventoryRead):
            return self._status_response(request, 'unavailable', 'Inventory acquisition read returned unsupported evidence')
        if inventory_read.outcome != INVENTORY_AVAILABLE:
            state = 'conflicting' if inventory_read.outcome == INVENTORY_CONFLICTING else 'unavailable'
            return self._status_response(request, state, inventory_read.reason)

        records = inventory_read.records
        if any(record.acquisition_date < request.period_start or record.acquisition_date >= request.period_end or record.acquisition_date > request.as_of for record in records):
            return self._status_response(request, 'conflicting', 'Inventory acquisition evidence falls outside the request boundary')
        if len({record.inventory_id for record in records}) != len(records):
            return self._status_response(request, 'conflicting', 'duplicate canonical Inventory identity')
        if not records:
            return PurchaseSourcePerformanceQueryResponse(
                request=request, evidence=(), source_domains=('inventory', 'sale_completion'),
                source_coverage=('complete',), provenance=(f'purchase-source-performance-provider:{request.request_id}:empty',),
            )

        try:
            sale_read = self._sale_completion_query.query(
                inventory_ids=tuple(sorted(record.inventory_id for record in records)),
                as_of=_at_utc_end(request.as_of),
                completed_from=_at_utc_start(request.period_start),
                completed_until=_at_utc_start(request.period_end),
            )
        except Exception:
            return self._status_response(request, 'unavailable', 'sale-completion read dependency unavailable')

        if not isinstance(sale_read, SaleCompletionRepositoryRead):
            return self._status_response(request, 'unavailable', 'sale-completion read returned unsupported response')

        result = sale_read.result
        if isinstance(result, (SaleCompletionUnavailable, SaleCompletionConflict)):
            state = 'conflicting' if isinstance(result, SaleCompletionConflict) else 'unavailable'
            diagnostic = self._diagnostic_reason(sale_read.diagnostic)
            reason = result.reason_code if not diagnostic else f'{result.reason_code}; {diagnostic}'
            return self._status_response(request, state, reason)
        if not isinstance(result, SaleCompletionAvailable):
            return self._status_response(request, 'unavailable', 'sale-completion read returned unsupported result')

        expected_as_of = _at_utc_end(request.as_of)
        expected_from = _at_utc_start(request.period_start)
        expected_until = _at_utc_start(request.period_end)
        coverage = getattr(result, 'coverage', None)
        expected_inventory_ids = tuple(sorted(record.inventory_id for record in records))
        if (
            coverage is None
            or getattr(coverage, 'completeness', None) is not SaleCompletionCompleteness.COMPLETE
            or getattr(coverage, 'requested_inventory_ids', None) != expected_inventory_ids
            or getattr(coverage, 'requested_sale_ids', None) != ()
            or getattr(coverage, 'as_of', None) != expected_as_of
            or getattr(coverage, 'completed_from', None) != expected_from
            or getattr(coverage, 'completed_until', None) != expected_until
        ):
            return self._status_response(request, 'conflicting', 'sale-completion coverage does not exactly match the requested Inventory identity and time boundaries')
        expected_ids = {record.inventory_id for record in records}
        if any(item.inventory_id not in expected_ids for item in result.evidence):
            return self._status_response(request, 'conflicting', 'sale-completion evidence returned an unrelated Inventory identity')

        # The sale-completion read includes lineage history. Only terminal evidence
        # is active; a completed parent with a refund, reversal, or supersession
        # child must not continue contributing completed units.
        parent_ids = {item.lineage_parent_evidence_id for item in result.evidence if item.lineage_parent_evidence_id is not None}
        active_evidence = tuple(
            item for item in result.evidence
            if item.sale_completion_evidence_id not in parent_ids
        )
        completed_by_inventory: dict[str, int] = {}
        for item in active_evidence:
            if item.lifecycle_state.value == 'completed':
                completed_by_inventory[item.inventory_id] = completed_by_inventory.get(item.inventory_id, 0) + (item.completed_unit_quantity or 0)
        acquired_by_source: dict[str, int] = {}
        completed_by_source: dict[str, int] = {}
        for record in records:
            acquired_by_source[record.purchase_source_label] = acquired_by_source.get(record.purchase_source_label, 0) + record.acquired_units
            completed_by_source[record.purchase_source_label] = completed_by_source.get(record.purchase_source_label, 0) + completed_by_inventory.get(record.inventory_id, 0)
        if any(completed_by_source[label] > acquired_by_source[label] for label in acquired_by_source):
            return self._status_response(request, 'conflicting', 'completed sale units exceed acquired Inventory units')

        provenance_base = f'purchase-source-performance-provider:{request.request_id}'
        evidence = tuple(
            PurchaseSourcePerformanceEvidence(
                purchase_source_label=label,
                acquired_units=acquired_by_source[label],
                completed_sale_units=completed_by_source[label],
                source_domains=('inventory', 'sale_completion'),
                source_coverage=('complete',),
                provenance=(f'{provenance_base}:inventory', f'{provenance_base}:sale_completion'),
                reason='complete Inventory acquisition and sale-completion coverage',
            )
            for label in sorted(acquired_by_source, key=lambda value: (value.casefold(), value))
        )
        return PurchaseSourcePerformanceQueryResponse(
            request=request, evidence=evidence, source_domains=('inventory', 'sale_completion'),
            source_coverage=('complete',), provenance=(f'{provenance_base}:inventory', f'{provenance_base}:sale_completion'),
        )

    @staticmethod
    def _diagnostic_reason(diagnostic: SaleCompletionRepositoryDiagnostic | None) -> str:
        if diagnostic is None:
            return ''
        if not isinstance(diagnostic, SaleCompletionRepositoryDiagnostic):
            return 'diagnostic=unsupported'
        return f'diagnostic_evidence_ids={diagnostic.evidence_ids}'

    @staticmethod
    def _status_response(request: PurchaseSourcePerformanceRequest, state: str, reason: str) -> PurchaseSourcePerformanceQueryResponse:
        label = 'Conflicting' if state == 'conflicting' else 'Unavailable'
        return PurchaseSourcePerformanceQueryResponse(
            request=request,
            evidence=(PurchaseSourcePerformanceEvidence(
                purchase_source_label=label, acquired_units=None, completed_sale_units=None,
                source_domains=('inventory', 'sale_completion'), source_coverage=(state,),
                provenance=(f'purchase-source-performance-provider:{request.request_id}:{state}',),
                evidence_state=state, reason=reason,
            ),),
            source_domains=('inventory', 'sale_completion'), source_coverage=(state,),
            provenance=(f'purchase-source-performance-provider:{request.request_id}:{state}',),
        )
