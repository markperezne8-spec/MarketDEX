from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from reports.purchase_source_performance_contract import (
    OUTCOME_CONFLICT,
    OUTCOME_INVALID_REQUEST,
    OUTCOME_UNAVAILABLE,
    OUTCOME_VALID,
    OUTCOME_ZERO_SELL_THROUGH,
    PurchaseSourcePerformanceRequest,
    PurchaseSourcePerformanceResult,
    PurchaseSourcePerformanceResultCollection,
)


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformanceEvidence:
    """Immutable calculator input for one exact purchase-source label."""

    purchase_source_label: str
    acquired_units: int | None
    completed_sale_units: int | None
    source_domains: tuple[str, ...]
    source_coverage: tuple[str, ...]
    provenance: tuple[str, ...]
    evidence_state: str = 'valid'
    reason: str = 'Prepared purchase-source evidence.'

    def __post_init__(self) -> None:
        label = str(self.purchase_source_label).strip()
        if not label:
            raise ValueError('purchase_source_label is required')
        if self.evidence_state not in ('valid', 'unavailable', 'conflicting'):
            raise ValueError('evidence_state must be valid, unavailable, or conflicting')
        for field_name in ('acquired_units', 'completed_sale_units'):
            value = getattr(self, field_name)
            if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
                raise TypeError(f'{field_name} must be an integer or None')
        if not self.source_domains or not self.source_coverage or not self.provenance:
            raise ValueError('source domains, coverage, and provenance are required')
        if not str(self.reason).strip():
            raise ValueError('reason is required')
        object.__setattr__(self, 'purchase_source_label', label)
        object.__setattr__(self, 'source_domains', tuple(self.source_domains))
        object.__setattr__(self, 'source_coverage', tuple(self.source_coverage))
        object.__setattr__(self, 'provenance', tuple(self.provenance))
        object.__setattr__(self, 'reason', str(self.reason).strip())


def calculate_purchase_source_performance(
    request: PurchaseSourcePerformanceRequest,
    evidence: PurchaseSourcePerformanceEvidence,
) -> PurchaseSourcePerformanceResult:
    """Return one validated fail-closed result without external reads or side effects."""

    if not isinstance(request, PurchaseSourcePerformanceRequest):
        raise TypeError('request must be a PurchaseSourcePerformanceRequest')
    if not isinstance(evidence, PurchaseSourcePerformanceEvidence):
        raise TypeError('evidence must be PurchaseSourcePerformanceEvidence')

    common = dict(
        request=request,
        reason=evidence.reason,
        source_domains=evidence.source_domains,
        source_coverage=evidence.source_coverage,
        provenance=evidence.provenance,
        purchase_source_label=evidence.purchase_source_label,
    )

    if evidence.evidence_state == 'unavailable':
        return PurchaseSourcePerformanceResult(
            outcome=OUTCOME_UNAVAILABLE,
            evidence_state='unavailable',
            **common,
        )
    if evidence.evidence_state == 'conflicting':
        return PurchaseSourcePerformanceResult(
            outcome=OUTCOME_CONFLICT,
            evidence_state='conflicting',
            **common,
        )

    acquired = evidence.acquired_units
    completed = evidence.completed_sale_units
    if acquired is None or completed is None:
        return PurchaseSourcePerformanceResult(
            outcome=OUTCOME_UNAVAILABLE,
            evidence_state='unavailable',
            **common,
        )
    if acquired <= 0 or completed < 0 or completed > acquired:
        return PurchaseSourcePerformanceResult(
            outcome=OUTCOME_INVALID_REQUEST,
            evidence_state='valid',
            **common,
        )

    ratio = Decimal(completed) / Decimal(acquired)
    outcome = OUTCOME_ZERO_SELL_THROUGH if completed == 0 else OUTCOME_VALID
    return PurchaseSourcePerformanceResult(
        outcome=outcome,
        evidence_state='valid',
        acquired_units=acquired,
        completed_sale_units=completed,
        remaining_unsold_units=acquired - completed,
        sell_through_ratio=ratio,
        sell_through_percentage=ratio * Decimal('100'),
        **common,
    )


def calculate_purchase_source_performance_collection(
    request: PurchaseSourcePerformanceRequest,
    evidence: tuple[PurchaseSourcePerformanceEvidence, ...],
) -> PurchaseSourcePerformanceResultCollection:
    """Calculate and deterministically order a tuple of grouped evidence values."""

    if not isinstance(evidence, tuple) or any(
        not isinstance(item, PurchaseSourcePerformanceEvidence) for item in evidence
    ):
        raise TypeError('evidence must be a tuple of PurchaseSourcePerformanceEvidence values')
    return PurchaseSourcePerformanceResultCollection(
        request=request,
        results=tuple(calculate_purchase_source_performance(request, item) for item in evidence),
    )
