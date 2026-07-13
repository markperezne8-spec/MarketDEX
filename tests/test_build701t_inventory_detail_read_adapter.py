from contextlib import nullcontext

from services.inventory_detail_read import (
    INVENTORY_DETAIL_FOUND,
    INVENTORY_DETAIL_NOT_FOUND,
    INVENTORY_DETAIL_UNAVAILABLE,
    InventoryDetailReadAdapter,
    InventoryDetailReadBoundary,
    InventoryDetailReadRequest,
)


class _Cursor:
    def __init__(self, row: dict[str, object] | None) -> None:
        self._row = row

    def fetchone(self) -> dict[str, object] | None:
        return self._row


class _Connection:
    def __init__(self, row: dict[str, object] | None) -> None:
        self.row = row
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def execute(self, sql: str, arguments: tuple[str, ...]) -> _Cursor:
        self.calls.append((sql, arguments))
        return _Cursor(self.row)


def _adapter(row: dict[str, object] | None) -> tuple[InventoryDetailReadAdapter, _Connection]:
    connection = _Connection(row)
    return InventoryDetailReadAdapter(lambda: nullcontext(connection)), connection


def test_build701t_adapter_reads_current_inventory_detail_without_mutation() -> None:
    adapter, connection = _adapter(
        {
            'asset_id': 'asset-001',
            'asset_name': 'Sample Card',
            'state': 'COMPLETED',
            'quantity': 1,
            'purchase_date': '2025-01-01',
            'storage_location': 'A-1',
        }
    )

    result = adapter.get_inventory_detail(InventoryDetailReadRequest('asset-001'))

    assert isinstance(adapter, InventoryDetailReadBoundary)
    assert result.outcome == INVENTORY_DETAIL_FOUND
    assert result.record is not None
    assert result.record.purchase_date_raw == '2025-01-01'
    assert result.record.current_quantity == 1
    assert connection.calls[0][1] == ('asset-001',)
    assert connection.calls[0][0].startswith('SELECT ')
    assert 'INSERT' not in connection.calls[0][0]


def test_build701t_adapter_returns_not_found_and_unavailable_explicitly() -> None:
    missing, _ = _adapter(None)

    def unavailable_connection():
        raise RuntimeError('not available')

    unavailable = InventoryDetailReadAdapter(unavailable_connection)

    assert missing.get_inventory_detail(InventoryDetailReadRequest('asset-001')).outcome == INVENTORY_DETAIL_NOT_FOUND
    assert unavailable.get_inventory_detail(InventoryDetailReadRequest('asset-001')).outcome == INVENTORY_DETAIL_UNAVAILABLE
