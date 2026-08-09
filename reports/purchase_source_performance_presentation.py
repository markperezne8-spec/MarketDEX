from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from reports.purchase_source_performance_query import PurchaseSourcePerformanceQueryResponse


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformancePresentationRow:
    purchase_source_label: str
    outcome: str
    acquired_units: int | None
    completed_sale_units: int | None
    remaining_unsold_units: int | None
    sell_through_percentage: object | None
    evidence_state: str
    reason: str
    provenance: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformancePresentation:
    period_start: date
    period_end: date
    as_of: date
    source_coverage: tuple[str, ...]
    provenance: tuple[str, ...]
    rows: tuple[PurchaseSourcePerformancePresentationRow, ...]


def present_purchase_source_performance(
    response: PurchaseSourcePerformanceQueryResponse,
) -> PurchaseSourcePerformancePresentation:
    if not isinstance(response, PurchaseSourcePerformanceQueryResponse):
        raise TypeError('response must be PurchaseSourcePerformanceQueryResponse')
    request = response.request
    rows = tuple(
        PurchaseSourcePerformancePresentationRow(
            purchase_source_label=e.purchase_source_label,
            outcome=getattr(e, 'outcome', e.evidence_state),
            acquired_units=e.acquired_units,
            completed_sale_units=e.completed_sale_units,
            remaining_unsold_units=getattr(e, 'remaining_unsold_units', None),
            sell_through_percentage=getattr(e, 'sell_through_percentage', None),
            evidence_state=e.evidence_state,
            reason=e.reason,
            provenance=e.provenance,
        )
        for e in response.evidence
    )
    return PurchaseSourcePerformancePresentation(
        period_start=request.period_start,
        period_end=request.period_end,
        as_of=request.as_of,
        source_coverage=response.source_coverage,
        provenance=response.provenance,
        rows=rows,
    )
