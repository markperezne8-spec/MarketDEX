from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, ContextManager, Protocol, runtime_checkable


INVENTORY_DETAIL_FOUND = 'found'
INVENTORY_DETAIL_NOT_FOUND = 'not_found'
INVENTORY_DETAIL_UNAVAILABLE = 'unavailable'

INVENTORY_DETAIL_READ_OUTCOMES = frozenset(
    {
        INVENTORY_DETAIL_FOUND,
        INVENTORY_DETAIL_NOT_FOUND,
        INVENTORY_DETAIL_UNAVAILABLE,
    }
)


def _required_text(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f'{field_name} is required')
    return normalized


@dataclass(frozen=True, slots=True)
class InventoryDetailReadRequest:
    """Validated request for one Inventory-owned detail read."""

    inventory_position_id: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            'inventory_position_id',
            _required_text(self.inventory_position_id, 'inventory_position_id'),
        )


@dataclass(frozen=True, slots=True)
class InventoryDetailReadRecord:
    """Immutable Inventory-owned detail evidence with raw purchase-date text."""

    inventory_position_id: str
    asset_name: str
    current_quantity: int
    inventory_status: str
    purchase_date_raw: str
    storage_location: str
    source_domain: str = 'inventory'

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
        object.__setattr__(self, 'purchase_date_raw', str(self.purchase_date_raw).strip())
        object.__setattr__(self, 'storage_location', str(self.storage_location).strip())
        source_domain = _required_text(self.source_domain, 'source_domain').lower()
        if source_domain != 'inventory':
            raise ValueError('source_domain must remain inventory')
        object.__setattr__(self, 'source_domain', source_domain)


@dataclass(frozen=True, slots=True)
class InventoryDetailReadResult:
    """Immutable result from a future injected Inventory detail boundary."""

    outcome: str
    record: InventoryDetailReadRecord | None = None
    reason: str = ''

    def __post_init__(self) -> None:
        outcome = str(self.outcome).strip().lower()
        if outcome not in INVENTORY_DETAIL_READ_OUTCOMES:
            raise ValueError(f'unsupported Inventory detail outcome: {outcome}')
        object.__setattr__(self, 'outcome', outcome)
        if outcome == INVENTORY_DETAIL_FOUND and self.record is None:
            raise ValueError('found Inventory detail requires a record')
        if outcome != INVENTORY_DETAIL_FOUND and self.record is not None:
            raise ValueError('only found Inventory detail may contain a record')
        object.__setattr__(self, 'reason', str(self.reason).strip())

    @property
    def is_found(self) -> bool:
        return self.outcome == INVENTORY_DETAIL_FOUND


@runtime_checkable
class InventoryDetailReadBoundary(Protocol):
    """Read-only Inventory detail boundary; implementations must not mutate authority."""

    def get_inventory_detail(
        self,
        request: InventoryDetailReadRequest,
    ) -> InventoryDetailReadResult:
        """Return explicit detail evidence for one Inventory position."""


class InventoryDetailReadAdapter:
    """Injected, read-only Inventory detail adapter."""

    def __init__(self, open_read_connection: Callable[[], ContextManager[Any]]) -> None:
        self._open_read_connection = open_read_connection

    def get_inventory_detail(
        self,
        request: InventoryDetailReadRequest,
    ) -> InventoryDetailReadResult:
        try:
            with self._open_read_connection() as connection:
                row = connection.execute(
                    "SELECT a.asset_id, a.asset_name, a.state, i.quantity, "
                    "COALESCE(b.purchase_date, '') AS purchase_date, "
                    "COALESCE(b.storage_location, '') AS storage_location "
                    "FROM assets a JOIN inventory_authority i ON i.asset_id = a.asset_id "
                    "LEFT JOIN inventory_business_details b ON b.asset_id = a.asset_id "
                    "WHERE a.asset_id = ?",
                    (request.inventory_position_id,),
                ).fetchone()
            if row is None:
                return InventoryDetailReadResult(
                    INVENTORY_DETAIL_NOT_FOUND,
                    reason='no Inventory detail evidence',
                )
            return InventoryDetailReadResult(
                INVENTORY_DETAIL_FOUND,
                InventoryDetailReadRecord(
                    inventory_position_id=row['asset_id'],
                    asset_name=row['asset_name'],
                    current_quantity=int(row['quantity']),
                    inventory_status=row['state'],
                    purchase_date_raw=row['purchase_date'],
                    storage_location=row['storage_location'],
                ),
                reason='current Inventory detail',
            )
        except Exception:
            return InventoryDetailReadResult(
                INVENTORY_DETAIL_UNAVAILABLE,
                reason='Inventory read dependency unavailable',
            )
