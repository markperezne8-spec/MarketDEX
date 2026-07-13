from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from services.inventory_product_link_read import (
    INVENTORY_PRODUCT_LINK_READ_OUTCOMES,
    PRODUCT_LINK_CONFLICTING,
    PRODUCT_LINK_FOUND,
    PRODUCT_LINK_UNAVAILABLE,
    PRODUCT_LINK_UNLINKED,
    InventoryProductLinkReadBoundary,
    InventoryProductLinkReadRequest,
    InventoryProductLinkReadResult,
)


def test_build701p_linked_result_exposes_one_canonical_product_id() -> None:
    result = InventoryProductLinkReadResult(PRODUCT_LINK_FOUND, 'product-001', 'verified')

    assert result.outcome == PRODUCT_LINK_FOUND
    assert result.product_id == 'product-001'
    assert result.is_linked is True
    with pytest.raises(FrozenInstanceError):
        result.product_id = 'product-002'  # type: ignore[misc]


@pytest.mark.parametrize(
    'outcome',
    (PRODUCT_LINK_UNLINKED, PRODUCT_LINK_CONFLICTING, PRODUCT_LINK_UNAVAILABLE),
)
def test_build701p_nonlinked_results_hide_product_identity(outcome: str) -> None:
    result = InventoryProductLinkReadResult(outcome, reason='boundary outcome')

    assert result.product_id is None
    assert result.is_linked is False


def test_build701p_result_rejects_guessed_or_missing_product_identity() -> None:
    with pytest.raises(ValueError, match='requires product_id'):
        InventoryProductLinkReadResult(PRODUCT_LINK_FOUND)
    with pytest.raises(ValueError, match='only linked'):
        InventoryProductLinkReadResult(PRODUCT_LINK_UNLINKED, 'product-001')
    with pytest.raises(ValueError, match='unsupported'):
        InventoryProductLinkReadResult('not_found')


def test_build701p_protocol_is_structural_and_persistence_free() -> None:
    class FixedBoundary:
        def get_product_link(
            self,
            request: InventoryProductLinkReadRequest,
        ) -> InventoryProductLinkReadResult:
            assert request.inventory_position_id == 'asset-001'
            return InventoryProductLinkReadResult(PRODUCT_LINK_UNAVAILABLE, reason='not configured')

    source = Path('services/inventory_product_link_read.py').read_text(encoding='utf-8').lower()

    assert isinstance(FixedBoundary(), InventoryProductLinkReadBoundary)
    assert FixedBoundary().get_product_link(InventoryProductLinkReadRequest('asset-001')).outcome == PRODUCT_LINK_UNAVAILABLE
    assert INVENTORY_PRODUCT_LINK_READ_OUTCOMES == frozenset(
        {PRODUCT_LINK_FOUND, PRODUCT_LINK_UNLINKED, PRODUCT_LINK_CONFLICTING, PRODUCT_LINK_UNAVAILABLE}
    )
    assert 'databasemanager' not in source
    assert 'sqlite' not in source
    assert 'repository' not in source
    assert 'http' not in source
