from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from services.inventory_detail_read import (
    INVENTORY_DETAIL_FOUND,
    INVENTORY_DETAIL_NOT_FOUND,
    INVENTORY_DETAIL_UNAVAILABLE,
    InventoryDetailReadBoundary,
    InventoryDetailReadRecord,
    InventoryDetailReadRequest,
    InventoryDetailReadResult,
)


def _record() -> InventoryDetailReadRecord:
    return InventoryDetailReadRecord(
        inventory_position_id='asset-001',
        asset_name='Sample Card',
        current_quantity=1,
        inventory_status='COMPLETED',
        purchase_date_raw=' 2025-01-01 ',
        storage_location=' A-1 ',
    )


def test_build701s_found_result_preserves_inventory_owned_raw_evidence() -> None:
    record = _record()
    result = InventoryDetailReadResult(INVENTORY_DETAIL_FOUND, record, 'current detail')

    assert record.inventory_status == 'completed'
    assert record.purchase_date_raw == '2025-01-01'
    assert record.storage_location == 'A-1'
    assert record.source_domain == 'inventory'
    assert result.record is record
    assert result.is_found is True
    with pytest.raises(FrozenInstanceError):
        record.asset_name = 'Other'  # type: ignore[misc]


@pytest.mark.parametrize('outcome', (INVENTORY_DETAIL_NOT_FOUND, INVENTORY_DETAIL_UNAVAILABLE))
def test_build701s_nonfound_results_hide_detail_record(outcome: str) -> None:
    result = InventoryDetailReadResult(outcome, reason='boundary outcome')

    assert result.record is None
    assert result.is_found is False


def test_build701s_request_and_result_reject_invalid_values() -> None:
    with pytest.raises(ValueError, match='inventory_position_id is required'):
        InventoryDetailReadRequest(' ')
    with pytest.raises(ValueError, match='only found'):
        InventoryDetailReadResult(INVENTORY_DETAIL_NOT_FOUND, _record())
    with pytest.raises(ValueError, match='source_domain'):
        InventoryDetailReadRecord(
            'asset-001', 'Sample Card', 1, 'completed', '', '', source_domain='product'
        )


def test_build701s_protocol_is_structural_and_persistence_free() -> None:
    class FixedBoundary:
        def get_inventory_detail(self, request: InventoryDetailReadRequest) -> InventoryDetailReadResult:
            assert request.inventory_position_id == 'asset-001'
            return InventoryDetailReadResult(INVENTORY_DETAIL_UNAVAILABLE, reason='not configured')

    source = Path('services/inventory_detail_read.py').read_text(encoding='utf-8').lower()

    assert isinstance(FixedBoundary(), InventoryDetailReadBoundary)
    assert FixedBoundary().get_inventory_detail(InventoryDetailReadRequest('asset-001')).outcome == INVENTORY_DETAIL_UNAVAILABLE
    assert 'databasemanager' not in source
    assert 'sqlite' not in source
    assert 'repository' not in source
    assert 'http' not in source
