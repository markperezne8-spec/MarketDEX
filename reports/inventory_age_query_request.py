from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class InventoryAgeReportQueryRequest:
    """Validated immutable request for one Inventory Age report query."""

    inventory_position_id: str
    as_of_date: date

    def __post_init__(self) -> None:
        position_id = str(self.inventory_position_id).strip()
        if not position_id:
            raise ValueError('inventory_position_id is required')
        if not isinstance(self.as_of_date, date):
            raise TypeError('as_of_date must be a date')
        object.__setattr__(self, 'inventory_position_id', position_id)
