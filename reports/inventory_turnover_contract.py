from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Iterable


INVENTORY_TURNOVER_REPORT_ID = 'inventory-turnover'
INVENTORY_TURNOVER_FORMULA_ID = 'inventory-turnover-units-v1'
BUSINESS_INVENTORY_SCOPE = 'business_inventory'

GROUP_BY_PRODUCT_ID = 'product_id'
GROUP_BY_PRODUCT_CATEGORY = 'product_category'
GROUP_BY_STORAGE_LOCATION = 'storage_location'
GROUP_BY_PURCHASE_SOURCE = 'purchase_source'

INVENTORY_TURNOVER_GROUPINGS = frozenset(
    {
        GROUP_BY_PRODUCT_ID,
        GROUP_BY_PRODUCT_CATEGORY,
        GROUP_BY_STORAGE_LOCATION,
        GROUP_BY_PURCHASE_SOURCE,
    }
)

OUTCOME_VALID = 'valid'
OUTCOME_ZERO_TURNOVER = 'zero_turnover'
OUTCOME_NO_ELIGIBLE_INVENTORY = 'no_eligible_inventory'
OUTCOME_IN_PROGRESS = 'in_progress'
OUTCOME_UNAVAILABLE = 'unavailable'
OUTCOME_CONFLICT = 'conflict'
OUTCOME_INVALID_REQUEST = 'invalid_request'

INVENTORY_TURNOVER_OUTCOMES = frozenset(
    {
        OUTCOME_VALID,
        OUTCOME_ZERO_TURNOVER,
        OUTCOME_NO_ELIGIBLE_INVENTORY,
        OUTCOME_IN_PROGRESS,
        OUTCOME_UNAVAILABLE,
        OUTCOME_CONFLICT,
        OUTCOME_INVALID_REQUEST,
    }
)

_NUMERIC_FIELDS = (
    'opening_eligible_inventory_units',
    'closing_eligible_inventory_units',
    'average_eligible_inventory_units',
    'completed_sale_units',
    'turnover_ratio',
    'turnover_percentage',
)


def _normalize_token(value: str, field_name: str) -> str:
    if value is None:
        raise ValueError(f'{field_name} is required')
    normalized = str(value).strip().lower().replace(' ', '_').replace('-', '_')
    if not normalized:
        raise ValueError(f'{field_name} is required')
    return normalized


def _required_text(value: str, field_name: str) -> str:
    if value is None:
        raise ValueError(f'{field_name} is required')
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f'{field_name} is required')
    return normalized


def _optional_token(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_token(value, field_name)


def _normalized_values(values: Iterable[str], field_name: str) -> tuple[str, ...]:
    if values is None or isinstance(values, str):
        raise TypeError(f'{field_name} must be an iterable of text values')
    normalized = tuple(
        sorted(
            {
                _normalize_token(value, field_name)
                for value in values
            }
        )
    )
    if not normalized:
        raise ValueError(f'at least one {field_name} is required')
    return normalized


def _require_date(value: date, field_name: str) -> date:
    if not isinstance(value, date):
        raise TypeError(f'{field_name} must be a date')
    return value


def _optional_non_negative_int(value: int | None, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f'{field_name} must be an integer')
    if value < 0:
        raise ValueError(f'{field_name} must be non-negative')
    return value


def _optional_non_negative_decimal(value: Decimal | int | str | None, field_name: str) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise TypeError(f'{field_name} must be numeric')
    try:
        normalized = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TypeError(f'{field_name} must be numeric') from exc
    if normalized < 0:
        raise ValueError(f'{field_name} must be non-negative')
    return normalized


@dataclass(frozen=True, slots=True)
class InventoryTurnoverReportRequest:
    """Immutable request contract for the Inventory Turnover report."""

    period_start: date
    period_end: date
    as_of: date
    source_coverage_required: tuple[str, ...]
    report_id: str = INVENTORY_TURNOVER_REPORT_ID
    formula_id: str = INVENTORY_TURNOVER_FORMULA_ID
    scope: str = BUSINESS_INVENTORY_SCOPE
    group_by: str | None = None
    include_in_progress_period: bool = False

    def __post_init__(self) -> None:
        report_id = _normalize_token(self.report_id, 'report_id').replace('_', '-')
        if report_id != INVENTORY_TURNOVER_REPORT_ID:
            raise ValueError(
                f'report_id must be {INVENTORY_TURNOVER_REPORT_ID}'
            )

        formula_id = _normalize_token(self.formula_id, 'formula_id').replace('_', '-')
        if formula_id != INVENTORY_TURNOVER_FORMULA_ID:
            raise ValueError(
                f'formula_id must be {INVENTORY_TURNOVER_FORMULA_ID}'
            )

        period_start = _require_date(self.period_start, 'period_start')
        period_end = _require_date(self.period_end, 'period_end')
        if period_start >= period_end:
            raise ValueError('period_start must be before period_end')

        as_of = _require_date(self.as_of, 'as_of')
        scope = _normalize_token(self.scope, 'scope')
        if scope != BUSINESS_INVENTORY_SCOPE:
            raise ValueError(f'scope must be {BUSINESS_INVENTORY_SCOPE}')

        group_by = _optional_token(self.group_by, 'group_by')
        if group_by is not None and group_by not in INVENTORY_TURNOVER_GROUPINGS:
            raise ValueError(f'unsupported group_by: {group_by}')

        coverage = _normalized_values(
            self.source_coverage_required,
            'source_coverage_required',
        )

        object.__setattr__(self, 'report_id', report_id)
        object.__setattr__(self, 'formula_id', formula_id)
        object.__setattr__(self, 'period_start', period_start)
        object.__setattr__(self, 'period_end', period_end)
        object.__setattr__(self, 'as_of', as_of)
        object.__setattr__(self, 'scope', scope)
        object.__setattr__(self, 'group_by', group_by)
        object.__setattr__(self, 'source_coverage_required', coverage)
        object.__setattr__(
            self,
            'include_in_progress_period',
            bool(self.include_in_progress_period),
        )

    @property
    def request_id(self) -> str:
        """Deterministic identity for the immutable request vocabulary."""

        group = self.group_by or 'ungrouped'
        coverage = ','.join(self.source_coverage_required)
        in_progress = 'in_progress' if self.include_in_progress_period else 'closed_only'
        return '|'.join(
            (
                self.report_id,
                self.formula_id,
                self.period_start.isoformat(),
                self.period_end.isoformat(),
                self.scope,
                group,
                self.as_of.isoformat(),
                coverage,
                in_progress,
            )
        )


@dataclass(frozen=True, slots=True)
class InventoryTurnoverReportResult:
    """Immutable result contract for the Inventory Turnover report."""

    request: InventoryTurnoverReportRequest
    outcome: str
    reason: str
    source_domains: tuple[str, ...]
    source_coverage: tuple[str, ...]
    evidence_state: str
    provenance: tuple[str, ...]
    group_key: str | None = None
    group_label: str | None = None
    opening_eligible_inventory_units: int | None = None
    closing_eligible_inventory_units: int | None = None
    average_eligible_inventory_units: Decimal | int | str | None = None
    completed_sale_units: int | None = None
    turnover_ratio: Decimal | int | str | None = None
    turnover_percentage: Decimal | int | str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.request, InventoryTurnoverReportRequest):
            raise TypeError('request must be an InventoryTurnoverReportRequest')

        outcome = _normalize_token(self.outcome, 'outcome')
        if outcome not in INVENTORY_TURNOVER_OUTCOMES:
            raise ValueError(f'unsupported outcome: {outcome}')

        reason = _required_text(self.reason, 'reason')
        source_domains = _normalized_values(self.source_domains, 'source_domain')
        source_coverage = _normalized_values(self.source_coverage, 'source_coverage')
        evidence_state = _normalize_token(self.evidence_state, 'evidence_state')
        provenance = tuple(_required_text(item, 'provenance') for item in self.provenance)
        if not provenance:
            raise ValueError('at least one provenance is required')

        group_key = _optional_token(self.group_key, 'group_key')
        group_label = self.group_label.strip() if self.group_label is not None else None

        opening = _optional_non_negative_int(
            self.opening_eligible_inventory_units,
            'opening_eligible_inventory_units',
        )
        closing = _optional_non_negative_int(
            self.closing_eligible_inventory_units,
            'closing_eligible_inventory_units',
        )
        average = _optional_non_negative_decimal(
            self.average_eligible_inventory_units,
            'average_eligible_inventory_units',
        )
        completed = _optional_non_negative_int(
            self.completed_sale_units,
            'completed_sale_units',
        )
        ratio = _optional_non_negative_decimal(self.turnover_ratio, 'turnover_ratio')
        percentage = _optional_non_negative_decimal(
            self.turnover_percentage,
            'turnover_percentage',
        )

        object.__setattr__(self, 'outcome', outcome)
        object.__setattr__(self, 'reason', reason)
        object.__setattr__(self, 'source_domains', source_domains)
        object.__setattr__(self, 'source_coverage', source_coverage)
        object.__setattr__(self, 'evidence_state', evidence_state)
        object.__setattr__(self, 'provenance', provenance)
        object.__setattr__(self, 'group_key', group_key)
        object.__setattr__(self, 'group_label', group_label)
        object.__setattr__(self, 'opening_eligible_inventory_units', opening)
        object.__setattr__(self, 'closing_eligible_inventory_units', closing)
        object.__setattr__(self, 'average_eligible_inventory_units', average)
        object.__setattr__(self, 'completed_sale_units', completed)
        object.__setattr__(self, 'turnover_ratio', ratio)
        object.__setattr__(self, 'turnover_percentage', percentage)

        self._validate_outcome_fields()

    @property
    def report_id(self) -> str:
        return self.request.report_id

    @property
    def formula_id(self) -> str:
        return self.request.formula_id

    @property
    def request_id(self) -> str:
        return self.request.request_id

    @property
    def period_start(self) -> date:
        return self.request.period_start

    @property
    def period_end(self) -> date:
        return self.request.period_end

    @property
    def scope(self) -> str:
        return self.request.scope

    @property
    def as_of(self) -> date:
        return self.request.as_of

    @property
    def sort_key(self) -> tuple[str, str]:
        group = self.group_key or ''
        return (group, self.request_id)

    def _validate_outcome_fields(self) -> None:
        if self.outcome == OUTCOME_VALID:
            self._require_formula_fields()
            if self.average_eligible_inventory_units <= 0:
                raise ValueError('valid outcome requires average eligible units greater than zero')
            if self.completed_sale_units <= 0:
                raise ValueError('valid outcome requires completed sale units greater than zero')
            if self.turnover_ratio <= 0 or self.turnover_percentage <= 0:
                raise ValueError('valid outcome requires positive turnover values')
            return

        if self.outcome == OUTCOME_ZERO_TURNOVER:
            self._require_formula_fields()
            if self.average_eligible_inventory_units <= 0:
                raise ValueError('zero turnover requires average eligible units greater than zero')
            if self.completed_sale_units != 0:
                raise ValueError('zero turnover requires completed sale units equal zero')
            if self.turnover_ratio != 0 or self.turnover_percentage != 0:
                raise ValueError('zero turnover requires zero turnover values')
            return

        if self.outcome == OUTCOME_NO_ELIGIBLE_INVENTORY:
            required_zero = (
                self.opening_eligible_inventory_units,
                self.closing_eligible_inventory_units,
                self.average_eligible_inventory_units,
                self.completed_sale_units,
            )
            if any(value is None for value in required_zero):
                raise ValueError('no eligible inventory requires zero quantity evidence')
            if any(value != 0 for value in required_zero):
                raise ValueError('no eligible inventory requires zero quantity evidence')
            if self.turnover_ratio is not None or self.turnover_percentage is not None:
                raise ValueError('no eligible inventory must not expose turnover values')
            return

        self._reject_numeric_fields()

    def _require_formula_fields(self) -> None:
        for field_name in _NUMERIC_FIELDS:
            if getattr(self, field_name) is None:
                raise ValueError(f'{self.outcome} outcome requires {field_name}')

    def _reject_numeric_fields(self) -> None:
        provided = [
            field_name
            for field_name in _NUMERIC_FIELDS
            if getattr(self, field_name) is not None
        ]
        if provided:
            names = ', '.join(provided)
            raise ValueError(f'{self.outcome} outcome must not expose numeric fields: {names}')
