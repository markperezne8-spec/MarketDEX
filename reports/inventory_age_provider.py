from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable

from reports.inventory_age_input import (
    PRODUCT_LINK_LINKED,
    InventoryAgeInputRecord,
)
from services.inventory_detail_read import (
    INVENTORY_DETAIL_FOUND,
    INVENTORY_DETAIL_NOT_FOUND,
    InventoryDetailReadBoundary,
    InventoryDetailReadRequest,
)
from services.inventory_product_link_read import (
    PRODUCT_LINK_CONFLICTING as LINK_READ_CONFLICTING,
    PRODUCT_LINK_FOUND as LINK_READ_FOUND,
    PRODUCT_LINK_UNAVAILABLE as LINK_READ_UNAVAILABLE,
    PRODUCT_LINK_UNLINKED as LINK_READ_UNLINKED,
    InventoryProductLinkReadBoundary,
    InventoryProductLinkReadRequest,
)


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


class ApplicationInventoryAgeInputProvider:
    """Compose approved Inventory and CAP-005B reads without owning persistence."""

    def __init__(
        self,
        inventory_detail_reader: InventoryDetailReadBoundary,
        product_link_reader: InventoryProductLinkReadBoundary,
    ) -> None:
        self._inventory_detail_reader = inventory_detail_reader
        self._product_link_reader = product_link_reader

    def get_inventory_age_input(
        self,
        inventory_position_id: str,
        as_of_date: date,
    ) -> InventoryAgeInputProviderResult:
        inventory_position_id = str(inventory_position_id).strip()
        if not inventory_position_id:
            raise ValueError('inventory_position_id is required')
        if type(as_of_date) is not date:
            raise TypeError('as_of_date must be a date')

        try:
            detail_result = self._inventory_detail_reader.get_inventory_detail(
                InventoryDetailReadRequest(inventory_position_id)
            )
        except Exception:
            return InventoryAgeInputProviderResult(
                INPUT_UNAVAILABLE,
                reason='Inventory detail read dependency unavailable',
            )

        if detail_result.outcome == INVENTORY_DETAIL_NOT_FOUND:
            return InventoryAgeInputProviderResult(
                INPUT_NOT_FOUND,
                reason=detail_result.reason or 'Inventory detail not found',
            )
        if detail_result.outcome != INVENTORY_DETAIL_FOUND or detail_result.record is None:
            return InventoryAgeInputProviderResult(
                INPUT_UNAVAILABLE,
                reason=detail_result.reason or 'Inventory detail unavailable',
            )

        detail = detail_result.record
        if detail.inventory_status != 'completed':
            return InventoryAgeInputProviderResult(
                INPUT_NOT_FOUND,
                reason='Inventory position is not completed',
            )

        try:
            link_result = self._product_link_reader.get_product_link(
                InventoryProductLinkReadRequest(inventory_position_id)
            )
        except Exception:
            return InventoryAgeInputProviderResult(
                INPUT_UNAVAILABLE,
                reason='CAP-005B read dependency unavailable',
            )

        if link_result.outcome == LINK_READ_UNLINKED:
            return InventoryAgeInputProviderResult(
                INPUT_UNLINKED,
                reason=link_result.reason or 'Inventory position is unlinked',
            )
        if link_result.outcome == LINK_READ_CONFLICTING:
            return InventoryAgeInputProviderResult(
                INPUT_CONFLICTING,
                reason=link_result.reason or 'product-link evidence is conflicting',
            )
        if link_result.outcome == LINK_READ_UNAVAILABLE:
            return InventoryAgeInputProviderResult(
                INPUT_UNAVAILABLE,
                reason=link_result.reason or 'CAP-005B read dependency unavailable',
            )
        if link_result.outcome != LINK_READ_FOUND or link_result.product_id is None:
            return InventoryAgeInputProviderResult(
                INPUT_UNAVAILABLE,
                reason='CAP-005B read dependency returned unsupported evidence',
            )

        return InventoryAgeInputProviderResult(
            INPUT_FOUND,
            InventoryAgeInputRecord(
                inventory_position_id=detail.inventory_position_id,
                asset_name=detail.asset_name,
                current_quantity=detail.current_quantity,
                inventory_status=detail.inventory_status,
                purchase_date_raw=detail.purchase_date_raw,
                storage_location=detail.storage_location,
                product_link_state=PRODUCT_LINK_LINKED,
                product_id=link_result.product_id,
                as_of_date=as_of_date,
            ),
            reason='approved Inventory and CAP-005B evidence',
        )
