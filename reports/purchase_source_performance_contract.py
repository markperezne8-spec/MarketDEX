from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Iterable

PURCHASE_SOURCE_PERFORMANCE_REPORT_ID = 'purchase-source-performance'
PURCHASE_SOURCE_PERFORMANCE_FORMULA_ID = 'purchase-source-sell-through-units-v1'
BUSINESS_INVENTORY_SCOPE = 'business_inventory'
GROUP_BY_PURCHASE_SOURCE = 'purchase_source'

OUTCOME_VALID = 'valid'
OUTCOME_ZERO_SELL_THROUGH = 'zero_sell_through'
OUTCOME_UNAVAILABLE = 'unavailable'
OUTCOME_CONFLICT = 'conflict'
OUTCOME_INVALID_REQUEST = 'invalid_request'
PURCHASE_SOURCE_PERFORMANCE_OUTCOMES = frozenset({
    OUTCOME_VALID,
    OUTCOME_ZERO_SELL_THROUGH,
    OUTCOME_UNAVAILABLE,
    OUTCOME_CONFLICT,
    OUTCOME_INVALID_REQUEST,
})
EVIDENCE_STATES = frozenset({'valid', 'unavailable', 'conflicting'})


def _text(value: str, name: str) -> str:
    if value is None or not str(value).strip():
        raise ValueError(f'{name} is required')
    return str(value).strip()


def _token(value: str, name: str) -> str:
    return _text(value, name).lower().replace(' ', '_').replace('-', '_')


def _values(values: Iterable[str], name: str) -> tuple[str, ...]:
    if values is None or isinstance(values, str):
        raise TypeError(f'{name} must be an iterable of text values')
    result = tuple(sorted({_token(value, name) for value in values}))
    if not result:
        raise ValueError(f'at least one {name} is required')
    return result


def _non_negative_int(value: int | None, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f'{name} must be an integer')
    if value < 0:
        raise ValueError(f'{name} must be non-negative')
    return value


def _non_negative_decimal(value, name: str) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise TypeError(f'{name} must be numeric')
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TypeError(f'{name} must be numeric') from exc
    if result < 0:
        raise ValueError(f'{name} must be non-negative')
    return result


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformanceRequest:
    period_start: date
    period_end: date
    as_of: date
    source_coverage_required: tuple[str, ...]
    report_id: str = PURCHASE_SOURCE_PERFORMANCE_REPORT_ID
    formula_id: str = PURCHASE_SOURCE_PERFORMANCE_FORMULA_ID
    scope: str = BUSINESS_INVENTORY_SCOPE
    group_by: str = GROUP_BY_PURCHASE_SOURCE

    def __post_init__(self) -> None:
        if not isinstance(self.period_start, date) or not isinstance(self.period_end, date):
            raise TypeError('period boundaries must be dates')
        if self.period_start >= self.period_end:
            raise ValueError('period_start must be before period_end')
        if not isinstance(self.as_of, date):
            raise TypeError('as_of must be a date')
        if self.as_of < self.period_end:
            raise ValueError('as_of must be on or after period_end')
        report_id = _token(self.report_id, 'report_id').replace('_', '-')
        formula_id = _token(self.formula_id, 'formula_id').replace('_', '-')
        scope = _token(self.scope, 'scope')
        group_by = _token(self.group_by, 'group_by')
        if report_id != PURCHASE_SOURCE_PERFORMANCE_REPORT_ID:
            raise ValueError(f'report_id must be {PURCHASE_SOURCE_PERFORMANCE_REPORT_ID}')
        if formula_id != PURCHASE_SOURCE_PERFORMANCE_FORMULA_ID:
            raise ValueError(f'formula_id must be {PURCHASE_SOURCE_PERFORMANCE_FORMULA_ID}')
        if scope != BUSINESS_INVENTORY_SCOPE:
            raise ValueError(f'scope must be {BUSINESS_INVENTORY_SCOPE}')
        if group_by != GROUP_BY_PURCHASE_SOURCE:
            raise ValueError(f'group_by must be {GROUP_BY_PURCHASE_SOURCE}')
        object.__setattr__(self, 'report_id', report_id)
        object.__setattr__(self, 'formula_id', formula_id)
        object.__setattr__(self, 'scope', scope)
        object.__setattr__(self, 'group_by', group_by)
        object.__setattr__(self, 'source_coverage_required', _values(self.source_coverage_required, 'source_coverage_required'))

    @property
    def request_id(self) -> str:
        return '|'.join((self.report_id, self.formula_id, self.period_start.isoformat(), self.period_end.isoformat(), self.as_of.isoformat(), self.scope, self.group_by, ','.join(self.source_coverage_required)))


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformanceResult:
    request: PurchaseSourcePerformanceRequest
    outcome: str
    reason: str
    source_domains: tuple[str, ...]
    source_coverage: tuple[str, ...]
    evidence_state: str
    provenance: tuple[str, ...]
    purchase_source_label: str | None = None
    acquired_units: int | None = None
    completed_sale_units: int | None = None
    remaining_unsold_units: int | None = None
    sell_through_ratio: Decimal | int | str | None = None
    sell_through_percentage: Decimal | int | str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.request, PurchaseSourcePerformanceRequest):
            raise TypeError('request must be a PurchaseSourcePerformanceRequest')
        outcome = _token(self.outcome, 'outcome')
        if outcome not in PURCHASE_SOURCE_PERFORMANCE_OUTCOMES:
            raise ValueError(f'unsupported outcome: {outcome}')
        evidence_state = _token(self.evidence_state, 'evidence_state')
        if evidence_state not in EVIDENCE_STATES:
            raise ValueError(f'unsupported evidence_state: {evidence_state}')
        label = self.purchase_source_label.strip() if self.purchase_source_label is not None else None
        if label == '':
            label = None
        provenance = tuple(_text(item, 'provenance') for item in self.provenance)
        if not provenance:
            raise ValueError('at least one provenance is required')
        object.__setattr__(self, 'outcome', outcome)
        object.__setattr__(self, 'reason', _text(self.reason, 'reason'))
        object.__setattr__(self, 'source_domains', _values(self.source_domains, 'source_domain'))
        object.__setattr__(self, 'source_coverage', _values(self.source_coverage, 'source_coverage'))
        object.__setattr__(self, 'evidence_state', evidence_state)
        object.__setattr__(self, 'provenance', provenance)
        object.__setattr__(self, 'purchase_source_label', label)
        for field in ('acquired_units', 'completed_sale_units', 'remaining_unsold_units'):
            object.__setattr__(self, field, _non_negative_int(getattr(self, field), field))
        object.__setattr__(self, 'sell_through_ratio', _non_negative_decimal(self.sell_through_ratio, 'sell_through_ratio'))
        object.__setattr__(self, 'sell_through_percentage', _non_negative_decimal(self.sell_through_percentage, 'sell_through_percentage'))
        self._validate_outcome()

    def _validate_outcome(self) -> None:
        numeric = (self.acquired_units, self.completed_sale_units, self.remaining_unsold_units, self.sell_through_ratio, self.sell_through_percentage)
        if self.outcome in (OUTCOME_UNAVAILABLE, OUTCOME_CONFLICT, OUTCOME_INVALID_REQUEST):
            if any(value is not None for value in numeric):
                raise ValueError(f'{self.outcome} outcome must not expose numeric values')
            return
        if self.purchase_source_label is None:
            raise ValueError(f'{self.outcome} outcome requires purchase_source_label')
        if any(value is None for value in numeric):
            raise ValueError(f'{self.outcome} outcome requires all numeric values')
        if self.acquired_units <= 0:
            raise ValueError('acquired_units must be greater than zero')
        if self.remaining_unsold_units != self.acquired_units - self.completed_sale_units:
            raise ValueError('remaining_unsold_units must equal acquired_units - completed_sale_units')
        expected_ratio = Decimal(self.completed_sale_units) / Decimal(self.acquired_units)
        if self.sell_through_ratio != expected_ratio or self.sell_through_percentage != expected_ratio * Decimal('100'):
            raise ValueError('sell-through values must match the approved formula')
        if self.outcome == OUTCOME_VALID and self.completed_sale_units <= 0:
            raise ValueError('valid outcome requires completed_sale_units greater than zero')
        if self.outcome == OUTCOME_ZERO_SELL_THROUGH and self.completed_sale_units != 0:
            raise ValueError('zero_sell_through requires completed_sale_units equal zero')

    @property
    def sort_key(self) -> tuple[int, Decimal, int, int, str, str]:
        order = {OUTCOME_VALID: 0, OUTCOME_ZERO_SELL_THROUGH: 0, OUTCOME_UNAVAILABLE: 1, OUTCOME_CONFLICT: 2, OUTCOME_INVALID_REQUEST: 3}
        percentage = self.sell_through_percentage if self.sell_through_percentage is not None else Decimal('-1')
        label = self.purchase_source_label or ''
        return (order[self.outcome], -percentage, -(self.completed_sale_units or 0), -(self.acquired_units or 0), label.casefold(), label)


@dataclass(frozen=True, slots=True)
class PurchaseSourcePerformanceResultCollection:
    request: PurchaseSourcePerformanceRequest
    results: tuple[PurchaseSourcePerformanceResult, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.request, PurchaseSourcePerformanceRequest):
            raise TypeError('request must be a PurchaseSourcePerformanceRequest')
        if not isinstance(self.results, tuple) or any(not isinstance(item, PurchaseSourcePerformanceResult) for item in self.results):
            raise TypeError('results must be a tuple of PurchaseSourcePerformanceResult values')
        if any(item.request != self.request for item in self.results):
            raise ValueError('all results must belong to the collection request')
        object.__setattr__(self, 'results', tuple(sorted(self.results, key=lambda item: item.sort_key)))
