from contextlib import nullcontext

from services.inventory_product_link_read import (
    PRODUCT_LINK_CONFLICTING,
    PRODUCT_LINK_FOUND,
    PRODUCT_LINK_UNAVAILABLE,
    PRODUCT_LINK_UNLINKED,
    InventoryProductLinkReadAdapter,
    InventoryProductLinkReadBoundary,
    InventoryProductLinkReadRequest,
)


class _Cursor:
    def __init__(self, rows: list[dict[str, str]]) -> None:
        self._rows = rows

    def fetchall(self) -> list[dict[str, str]]:
        return self._rows


class _Connection:
    def __init__(self, rows: list[dict[str, str]]) -> None:
        self.rows = rows
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def execute(self, sql: str, arguments: tuple[str, ...]) -> _Cursor:
        self.calls.append((sql, arguments))
        return _Cursor(self.rows)


def _adapter(rows: list[dict[str, str]]) -> tuple[InventoryProductLinkReadAdapter, _Connection]:
    connection = _Connection(rows)
    return InventoryProductLinkReadAdapter(lambda: nullcontext(connection)), connection


def test_build701r_adapter_returns_one_verified_link_without_mutation() -> None:
    adapter, connection = _adapter([{'product_id': ' product-001 ', 'state': 'LINKED'}])

    result = adapter.get_product_link(InventoryProductLinkReadRequest('asset-001'))

    assert isinstance(adapter, InventoryProductLinkReadBoundary)
    assert result.outcome == PRODUCT_LINK_FOUND
    assert result.product_id == 'product-001'
    assert connection.calls == [
        (
            'SELECT product_id, state FROM inventory_product_links WHERE asset_id = ?',
            ('asset-001',),
        )
    ]


def test_build701r_adapter_returns_explicit_nonlinked_evidence() -> None:
    unlinked, _ = _adapter([])
    conflicting, _ = _adapter(
        [
            {'product_id': 'product-001', 'state': 'LINKED'},
            {'product_id': 'product-002', 'state': 'LINKED'},
        ]
    )
    invalid, _ = _adapter([{'product_id': '', 'state': 'LINKED'}])

    assert unlinked.get_product_link(InventoryProductLinkReadRequest('asset-001')).outcome == PRODUCT_LINK_UNLINKED
    assert conflicting.get_product_link(InventoryProductLinkReadRequest('asset-001')).outcome == PRODUCT_LINK_CONFLICTING
    assert invalid.get_product_link(InventoryProductLinkReadRequest('asset-001')).outcome == PRODUCT_LINK_CONFLICTING


def test_build701r_adapter_fails_closed_when_read_dependency_is_unavailable() -> None:
    def unavailable_connection():
        raise RuntimeError('not available')

    adapter = InventoryProductLinkReadAdapter(unavailable_connection)

    result = adapter.get_product_link(InventoryProductLinkReadRequest('asset-001'))

    assert result.outcome == PRODUCT_LINK_UNAVAILABLE
    assert result.product_id is None
