from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from services.inventory_product_link_read import InventoryProductLinkReadRequest


def test_build701q_read_request_requires_one_normalized_inventory_position_id() -> None:
    request = InventoryProductLinkReadRequest('  asset-001  ')

    assert request.inventory_position_id == 'asset-001'
    with pytest.raises(ValueError, match='inventory_position_id is required'):
        InventoryProductLinkReadRequest('   ')
    with pytest.raises(FrozenInstanceError):
        request.inventory_position_id = 'asset-002'  # type: ignore[misc]


def test_build701q_protocol_file_remains_ascii_and_persistence_free() -> None:
    source = Path('services/inventory_product_link_read.py').read_text(encoding='utf-8')

    assert source.isascii()
    assert 'DatabaseManager' not in source
    assert 'sqlite' not in source.lower()
