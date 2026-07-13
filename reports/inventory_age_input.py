from __future__ import annotations

from dataclasses import dataclass
from datetime import date


PRODUCT_LINK_LINKED = 'linked'
PRODUCT_LINK_UNLINKED = 'unlinked'
PRODUCT_LINK_CONFLICTING = 'conflicting'

PRODUCT_LINK_EVIDENCE_STATES = frozenset(
    {
        PRODUCT_LINK_LINKED,
        PRODUCT_LINK_UNLINKED,
        PRODUCT_LINK_CONFLICTING,
    }
)


def _required_text(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f'{field_name} is required')
    return normalized


@dataclass(frozen=True, slots=True)
class InventoryAgeInputRecord:
    """Validated, read-only input evidence for a future Inventory Age bridge."""

    inventory_position_id: str
    asset_name: str
    current_quantity: int
    inventory_status: str
    purchase_date_raw: str
    storage_location: str
    product_link_state: str
    as_of_date: date
    product_id: str | None = None
    inventory_source_domain: str = 'inventory'
    product_link_authority: str = 'inventory_product_link'

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            'inventory_position_id',
            _required_text(self.inventory_position_id, 'inventory_position_id'),
        )
        object.__setattr__(self, 'asset_name', _required_text(self.asset_name, 'asset_name'))
        if type(self.current_quantity) is not int or self.current_quantity < 0:
            raise ValueError('current_quantity must be a non-negative integer')
        object.__setattr__(
            self,
            'inventory_status',
            _required_text(self.inventory_status, 'inventory_status').lower(),
        )
        if type(self.as_of_date) is not date:
            raise TypeError('as_of_date must be a date')
        object.__setattr__(self, 'purchase_date_raw', self.purchase_date_raw.strip())
        object.__setattr__(self, 'storage_location', self.storage_location.strip())

        link_state = _required_text(self.product_link_state, 'product_link_state').lower()
        if link_state not in PRODUCT_LINK_EVIDENCE_STATES:
            raise ValueError(f'unsupported product_link_state: {link_state}')
        object.__setattr__(self, 'product_link_state', link_state)

        product_id = None if self.product_id is None else _required_text(self.product_id, 'product_id')
        if link_state == PRODUCT_LINK_LINKED and product_id is None:
            raise ValueError('linked product evidence requires product_id')
        if link_state != PRODUCT_LINK_LINKED and product_id is not None:
            raise ValueError('unlinked or conflicting product evidence must not contain product_id')
        object.__setattr__(self, 'product_id', product_id)

        inventory_source_domain = _required_text(
            self.inventory_source_domain,
            'inventory_source_domain',
        ).lower()
        if inventory_source_domain != 'inventory':
            raise ValueError('inventory_source_domain must remain inventory')
        object.__setattr__(self, 'inventory_source_domain', inventory_source_domain)

        product_link_authority = _required_text(
            self.product_link_authority,
            'product_link_authority',
        ).lower()
        if product_link_authority != 'inventory_product_link':
            raise ValueError('product_link_authority must remain inventory_product_link')
        object.__setattr__(self, 'product_link_authority', product_link_authority)

    @property
    def has_verified_product_link(self) -> bool:
        return self.product_link_state == PRODUCT_LINK_LINKED
