from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable


EVIDENCE_AVAILABLE = 'available'
EVIDENCE_UNAVAILABLE = 'unavailable'
EVIDENCE_INVALID = 'invalid'

INVENTORY_AGE_EVIDENCE_STATES = frozenset(
    {
        EVIDENCE_AVAILABLE,
        EVIDENCE_UNAVAILABLE,
        EVIDENCE_INVALID,
    }
)


def _required_text(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f'{field_name} is required')
    return normalized


def _require_date(value: date, field_name: str) -> date:
    if type(value) is not date:
        raise TypeError(f'{field_name} must be a date')
    return value


@dataclass(frozen=True, slots=True)
class InventoryAgeReportRow:
    """Immutable, Inventory-sourced row for read-only age reporting."""

    inventory_position_id: str
    product_id: str
    product_name: str
    current_quantity: int
    inventory_status: str
    as_of_date: date
    source_start_date: date | None
    age_days: int | None
    evidence_state: str
    storage_location: str = ''
    source_domain: str = 'inventory'

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            'inventory_position_id',
            _required_text(self.inventory_position_id, 'inventory_position_id'),
        )
        object.__setattr__(self, 'product_id', _required_text(self.product_id, 'product_id'))
        object.__setattr__(self, 'product_name', _required_text(self.product_name, 'product_name'))
        object.__setattr__(
            self,
            'inventory_status',
            _required_text(self.inventory_status, 'inventory_status').lower(),
        )
        object.__setattr__(self, 'as_of_date', _require_date(self.as_of_date, 'as_of_date'))
        if self.source_start_date is not None:
            object.__setattr__(
                self,
                'source_start_date',
                _require_date(self.source_start_date, 'source_start_date'),
            )
        if type(self.current_quantity) is not int or self.current_quantity < 0:
            raise ValueError('current_quantity must be a non-negative integer')

        evidence_state = _required_text(self.evidence_state, 'evidence_state').lower()
        if evidence_state not in INVENTORY_AGE_EVIDENCE_STATES:
            raise ValueError(f'unsupported evidence_state: {evidence_state}')
        object.__setattr__(self, 'evidence_state', evidence_state)

        if evidence_state == EVIDENCE_AVAILABLE:
            if self.source_start_date is None or self.age_days is None:
                raise ValueError('available evidence requires source_start_date and age_days')
            expected_age = (self.as_of_date - self.source_start_date).days
            if expected_age < 0 or self.age_days != expected_age:
                raise ValueError('available age_days must match the explicit dates')
        elif evidence_state == EVIDENCE_UNAVAILABLE:
            if self.source_start_date is not None or self.age_days is not None:
                raise ValueError('unavailable evidence must not contain source date or age')
        else:
            if self.source_start_date is None or self.source_start_date <= self.as_of_date:
                raise ValueError('invalid evidence requires a source date after the as-of date')
            if self.age_days is not None:
                raise ValueError('invalid evidence must not contain age_days')

        object.__setattr__(self, 'storage_location', self.storage_location.strip())
        source_domain = _required_text(self.source_domain, 'source_domain').lower()
        if source_domain != 'inventory':
            raise ValueError('Inventory Age rows must use Inventory source authority')
        object.__setattr__(self, 'source_domain', source_domain)


def derive_inventory_age_row(
    *,
    inventory_position_id: str,
    product_id: str,
    product_name: str,
    current_quantity: int,
    inventory_status: str,
    as_of_date: date,
    source_start_date: date | None,
    storage_location: str = '',
) -> InventoryAgeReportRow:
    """Derive one row from explicit dates without wall-clock or persistence access."""

    as_of = _require_date(as_of_date, 'as_of_date')
    if source_start_date is None:
        evidence_state = EVIDENCE_UNAVAILABLE
        age_days = None
    else:
        source_start = _require_date(source_start_date, 'source_start_date')
        if source_start > as_of:
            evidence_state = EVIDENCE_INVALID
            age_days = None
        else:
            evidence_state = EVIDENCE_AVAILABLE
            age_days = (as_of - source_start).days

    return InventoryAgeReportRow(
        inventory_position_id=inventory_position_id,
        product_id=product_id,
        product_name=product_name,
        current_quantity=current_quantity,
        inventory_status=inventory_status,
        as_of_date=as_of,
        source_start_date=source_start_date,
        age_days=age_days,
        evidence_state=evidence_state,
        storage_location=storage_location,
    )


def sort_inventory_age_rows(
    rows: Iterable[InventoryAgeReportRow],
) -> tuple[InventoryAgeReportRow, ...]:
    """Return invalid/unavailable evidence first, then available rows by age."""

    priority = {
        EVIDENCE_INVALID: 0,
        EVIDENCE_UNAVAILABLE: 1,
        EVIDENCE_AVAILABLE: 2,
    }
    return tuple(
        sorted(
            rows,
            key=lambda row: (
                priority[row.evidence_state],
                -(row.age_days or 0),
                row.product_name.casefold(),
                row.inventory_position_id,
            ),
        )
    )
