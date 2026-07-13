from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


PRODUCT_LINK_FOUND = 'linked'
PRODUCT_LINK_UNLINKED = 'unlinked'
PRODUCT_LINK_CONFLICTING = 'conflicting'
PRODUCT_LINK_UNAVAILABLE = 'unavailable'

INVENTORY_PRODUCT_LINK_READ_OUTCOMES = frozenset(
    {
        PRODUCT_LINK_FOUND,
        PRODUCT_LINK_UNLINKED,
        PRODUCT_LINK_CONFLICTING,
        PRODUCT_LINK_UNAVAILABLE,
    }
)


@dataclass(frozen=True, slots=True)
class InventoryProductLinkReadRequest:
    """Validated request for one CAP-005B asset-to-product read."""

    inventory_position_id: str

    def __post_init__(self) -> None:
        inventory_position_id = str(self.inventory_position_id).strip()
        if not inventory_position_id:
            raise ValueError('inventory_position_id is required')
        object.__setattr__(self, 'inventory_position_id', inventory_position_id)


@dataclass(frozen=True, slots=True)
class InventoryProductLinkReadResult:
    """Immutable CAP-005B evidence returned by an injected read boundary."""

    outcome: str
    product_id: str | None = None
    reason: str = ''

    def __post_init__(self) -> None:
        outcome = str(self.outcome).strip().lower()
        if outcome not in INVENTORY_PRODUCT_LINK_READ_OUTCOMES:
            raise ValueError(f'unsupported Inventory-Product Link outcome: {outcome}')
        object.__setattr__(self, 'outcome', outcome)

        product_id = None if self.product_id is None else str(self.product_id).strip()
        if outcome == PRODUCT_LINK_FOUND and not product_id:
            raise ValueError('linked product-link evidence requires product_id')
        if outcome != PRODUCT_LINK_FOUND and product_id is not None:
            raise ValueError('only linked product-link evidence may contain product_id')
        object.__setattr__(self, 'product_id', product_id)
        object.__setattr__(self, 'reason', str(self.reason).strip())

    @property
    def is_linked(self) -> bool:
        return self.outcome == PRODUCT_LINK_FOUND


@runtime_checkable
class InventoryProductLinkReadBoundary(Protocol):
    """Read-only CAP-005B boundary; implementations must not mutate authority."""

    def get_product_link(
        self,
        request: InventoryProductLinkReadRequest,
    ) -> InventoryProductLinkReadResult:
        """Return explicit asset-to-product evidence for one Inventory position."""
