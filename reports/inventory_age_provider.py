from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable

from reports.inventory_age_input import InventoryAgeInputRecord


INPUT_FOUND = 'found'
INPUT_NOT_FOUND = 'not_found'
INPUT_UNLINKED = 'unlinked'
INPUT_CONFLICTING = 'conflicting'
INPUT_UNAVAILABLE = 'unavailable'

INVENTORY_AGE_INPUT_OUTCOMES = frozenset(
    {
        INPUT_FOUND,
        INPUT_NOT_FOUND,
        INPUT_UNLINKED,
        INPUT_CONFLICTING,
        INPUT_UNAVAILABLE,
    }
)


@dataclass(frozen=True, slots=True)
class InventoryAgeInputProviderResult:
    """Immutable result of a future application-owned Inventory Age read."""

    outcome: str
    record: InventoryAgeInputRecord | None = None
    reason: str = ''

    def __post_init__(self) -> None:
        outcome = str(self.outcome).strip().lower()
        if outcome not in INVENTORY_AGE_INPUT_OUTCOMES:
            raise ValueError(f'unsupported Inventory Age input outcome: {outcome}')
        object.__setattr__(self, 'outcome', outcome)

        if outcome == INPUT_FOUND:
            if self.record is None or not self.record.has_verified_product_link:
                raise ValueError('found Inventory Age input requires a linked input record')
        elif self.record is not None:
            raise ValueError('only found Inventory Age input may contain a record')

        object.__setattr__(self, 'reason', str(self.reason).strip())

    @property
    def is_found(self) -> bool:
        return self.outcome == INPUT_FOUND


@runtime_checkable
class InventoryAgeInputProvider(Protocol):
    """Read-only boundary for future application-owned Inventory Age input."""

    def get_inventory_age_input(
        self,
        inventory_position_id: str,
        as_of_date: date,
    ) -> InventoryAgeInputProviderResult:
        """Return one immutable read result without mutating any authority."""
