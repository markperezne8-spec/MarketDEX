from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from reports.inventory_turnover_contract import (
    OUTCOME_NO_ELIGIBLE_INVENTORY,
    OUTCOME_VALID,
    OUTCOME_ZERO_TURNOVER,
    InventoryTurnoverReportResult,
)

_UNAVAILABLE = 'Unavailable'


@dataclass(frozen=True, slots=True)
class InventoryTurnoverPresentation:
    """Immutable display-ready projection of one turnover result."""

    outcome: str
    status: str
    reason: str
    period: str
    formula: str
    evidence: str
    opening_units: str
    closing_units: str
    average_units: str
    completed_sale_units: str
    turnover_ratio: str
    turnover_percentage: str



def _format_decimal(value: Decimal | None, places: int = 2) -> str:
    if value is None:
        return _UNAVAILABLE
    quantized = value.quantize(Decimal(1).scaleb(-places))
    text = format(quantized, 'f').rstrip('0').rstrip('.')
    return text or '0'



def _format_units(value: int | Decimal | None) -> str:
    if value is None:
        return _UNAVAILABLE
    if isinstance(value, Decimal):
        return _format_decimal(value)
    return str(value)



def present_inventory_turnover(
    result: InventoryTurnoverReportResult,
) -> InventoryTurnoverPresentation:
    """Map an immutable report result into deterministic display text."""
    if not isinstance(result, InventoryTurnoverReportResult):
        raise TypeError('result must be an InventoryTurnoverReportResult')

    numeric_allowed = result.outcome in {
        OUTCOME_VALID,
        OUTCOME_ZERO_TURNOVER,
        OUTCOME_NO_ELIGIBLE_INVENTORY,
    }

    ratio = _UNAVAILABLE
    percentage = _UNAVAILABLE
    if result.outcome in {OUTCOME_VALID, OUTCOME_ZERO_TURNOVER}:
        ratio = f'{_format_decimal(result.turnover_ratio)}×'
        percentage = f'{_format_decimal(result.turnover_percentage, 1)}%'

    return InventoryTurnoverPresentation(
        outcome=result.outcome,
        status=result.outcome.replace('_', ' ').upper(),
        reason=result.reason,
        period=f'{result.period_start.isoformat()} → {result.period_end.isoformat()}',
        formula=result.formula_id,
        evidence=f'{result.evidence_state} · {", ".join(result.source_coverage)}',
        opening_units=_format_units(result.opening_eligible_inventory_units)
        if numeric_allowed
        else _UNAVAILABLE,
        closing_units=_format_units(result.closing_eligible_inventory_units)
        if numeric_allowed
        else _UNAVAILABLE,
        average_units=_format_units(result.average_eligible_inventory_units)
        if numeric_allowed
        else _UNAVAILABLE,
        completed_sale_units=_format_units(result.completed_sale_units)
        if numeric_allowed
        else _UNAVAILABLE,
        turnover_ratio=ratio,
        turnover_percentage=percentage,
    )
