from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from reports.inventory_turnover_contract import (
    OUTCOME_CONFLICT,
    OUTCOME_NO_ELIGIBLE_INVENTORY,
    OUTCOME_UNAVAILABLE,
    OUTCOME_VALID,
    OUTCOME_ZERO_TURNOVER,
    InventoryTurnoverReportRequest,
    InventoryTurnoverReportResult,
)

EVIDENCE_AVAILABLE = 'available'
EVIDENCE_UNAVAILABLE = 'unavailable'
EVIDENCE_CONFLICTING = 'conflicting'
INVENTORY_TURNOVER_EVIDENCE_STATES = frozenset(
    {EVIDENCE_AVAILABLE, EVIDENCE_UNAVAILABLE, EVIDENCE_CONFLICTING}
)


@dataclass(frozen=True, slots=True)
class InventoryTurnoverEvidence:
    """Immutable, already-authorized quantity evidence for one report request."""

    opening_eligible_inventory_units: int | None
    closing_eligible_inventory_units: int | None
    completed_sale_units: int | None
    source_domains: tuple[str, ...]
    source_coverage: tuple[str, ...]
    provenance: tuple[str, ...]
    evidence_state: str = EVIDENCE_AVAILABLE
    reason: str = 'approved inventory-turnover evidence'

    def __post_init__(self) -> None:
        state = str(self.evidence_state).strip().lower()
        if state not in INVENTORY_TURNOVER_EVIDENCE_STATES:
            raise ValueError(f'unsupported inventory turnover evidence state: {state}')
        object.__setattr__(self, 'evidence_state', state)

        for field_name in (
            'opening_eligible_inventory_units',
            'closing_eligible_inventory_units',
            'completed_sale_units',
        ):
            value = getattr(self, field_name)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < 0
            ):
                raise ValueError(f'{field_name} must be a non-negative integer or None')

        if not self.source_domains or not self.source_coverage or not self.provenance:
            raise ValueError('source domains, coverage, and provenance are required')
        if not str(self.reason).strip():
            raise ValueError('reason is required')


class DeterministicInventoryTurnoverProvider:
    """Pure read-only provider that applies the approved unit-based formula."""

    def __init__(self, evidence: InventoryTurnoverEvidence) -> None:
        self._evidence = evidence

    def get_inventory_turnover_result(
        self,
        request: InventoryTurnoverReportRequest,
    ) -> InventoryTurnoverReportResult:
        if not isinstance(request, InventoryTurnoverReportRequest):
            raise TypeError('request must be an InventoryTurnoverReportRequest')

        evidence = self._evidence
        base = dict(
            request=request,
            reason=evidence.reason,
            source_domains=evidence.source_domains,
            source_coverage=evidence.source_coverage,
            evidence_state=evidence.evidence_state,
            provenance=evidence.provenance,
        )

        if request.group_by is not None:
            return InventoryTurnoverReportResult(
                outcome=OUTCOME_UNAVAILABLE,
                **{**base, 'reason': 'grouped Inventory Turnover results are not authorized'},
            )

        if evidence.evidence_state == EVIDENCE_UNAVAILABLE:
            return InventoryTurnoverReportResult(outcome=OUTCOME_UNAVAILABLE, **base)
        if evidence.evidence_state == EVIDENCE_CONFLICTING:
            return InventoryTurnoverReportResult(outcome=OUTCOME_CONFLICT, **base)

        opening = evidence.opening_eligible_inventory_units
        closing = evidence.closing_eligible_inventory_units
        completed = evidence.completed_sale_units
        if opening is None or closing is None or completed is None:
            return InventoryTurnoverReportResult(
                outcome=OUTCOME_UNAVAILABLE,
                **{**base, 'reason': 'required Inventory Turnover quantity evidence is missing'},
            )

        average = (Decimal(opening) + Decimal(closing)) / Decimal(2)
        quantity_fields = dict(
            opening_eligible_inventory_units=opening,
            closing_eligible_inventory_units=closing,
            average_eligible_inventory_units=average,
            completed_sale_units=completed,
        )

        if opening == 0 and closing == 0 and completed == 0:
            return InventoryTurnoverReportResult(
                outcome=OUTCOME_NO_ELIGIBLE_INVENTORY,
                **base,
                **quantity_fields,
            )

        if average == 0:
            return InventoryTurnoverReportResult(
                outcome=OUTCOME_CONFLICT,
                **{**base, 'reason': 'completed sale units conflict with zero eligible inventory'},
            )

        ratio = Decimal(completed) / average
        percentage = ratio * Decimal(100)
        formula_fields = dict(
            **quantity_fields,
            turnover_ratio=ratio,
            turnover_percentage=percentage,
        )

        if completed == 0:
            return InventoryTurnoverReportResult(
                outcome=OUTCOME_ZERO_TURNOVER,
                **base,
                **formula_fields,
            )

        return InventoryTurnoverReportResult(
            outcome=OUTCOME_VALID,
            **base,
            **formula_fields,
        )
