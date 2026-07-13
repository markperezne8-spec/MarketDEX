from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from reports.inventory_age import InventoryAgeReportRow
from reports.inventory_age_bridge import build_inventory_age_row_from_input
from reports.inventory_age_provider import (
    INPUT_CONFLICTING,
    INPUT_FOUND,
    INPUT_NOT_FOUND,
    INPUT_UNAVAILABLE,
    INPUT_UNLINKED,
    INVENTORY_AGE_INPUT_OUTCOMES,
    InventoryAgeInputProvider,
)


@dataclass(frozen=True, slots=True)
class InventoryAgeReportQueryResult:
    """Immutable result of one read-only Inventory Age query."""

    outcome: str
    row: InventoryAgeReportRow | None = None
    reason: str = ''

    def __post_init__(self) -> None:
        outcome = str(self.outcome).strip().lower()
        if outcome not in INVENTORY_AGE_INPUT_OUTCOMES:
            raise ValueError(f'unsupported Inventory Age query outcome: {outcome}')
        object.__setattr__(self, 'outcome', outcome)
        if outcome == INPUT_FOUND and self.row is None:
            raise ValueError('found Inventory Age query requires a report row')
        if outcome != INPUT_FOUND and self.row is not None:
            raise ValueError('only found Inventory Age query may contain a report row')
        object.__setattr__(self, 'reason', str(self.reason).strip())

    @property
    def is_found(self) -> bool:
        return self.outcome == INPUT_FOUND


class InventoryAgeReportQueryService:
    """Injected, read-only query service over approved Inventory Age input evidence."""

    def __init__(self, input_provider: InventoryAgeInputProvider) -> None:
        self._input_provider = input_provider

    def get_inventory_age_row(
        self,
        inventory_position_id: str,
        as_of_date: date,
    ) -> InventoryAgeReportQueryResult:
        try:
            provider_result = self._input_provider.get_inventory_age_input(
                inventory_position_id,
                as_of_date,
            )
        except Exception:
            return InventoryAgeReportQueryResult(
                INPUT_UNAVAILABLE,
                reason='Inventory Age input provider unavailable',
            )

        if provider_result.outcome != INPUT_FOUND:
            return InventoryAgeReportQueryResult(
                provider_result.outcome,
                reason=provider_result.reason,
            )
        if provider_result.record is None:
            return InventoryAgeReportQueryResult(
                INPUT_UNAVAILABLE,
                reason='Inventory Age input provider returned incomplete found evidence',
            )

        return InventoryAgeReportQueryResult(
            INPUT_FOUND,
            build_inventory_age_row_from_input(provider_result.record),
            reason=provider_result.reason,
        )
