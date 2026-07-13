from dataclasses import FrozenInstanceError
from datetime import date
from pathlib import Path

import pytest

from reports import (
    INPUT_CONFLICTING,
    INPUT_FOUND,
    INPUT_NOT_FOUND,
    INPUT_UNAVAILABLE,
    INPUT_UNLINKED,
    INVENTORY_AGE_INPUT_OUTCOMES,
    InventoryAgeInputProvider,
    InventoryAgeInputProviderResult,
    InventoryAgeInputRecord,
    PRODUCT_LINK_LINKED,
)


def _linked_record() -> InventoryAgeInputRecord:
    return InventoryAgeInputRecord(
        inventory_position_id='asset-001',
        asset_name='Sample Card',
        current_quantity=1,
        inventory_status='active',
        purchase_date_raw='2025-01-01',
        storage_location='A-1',
        product_link_state=PRODUCT_LINK_LINKED,
        product_id='product-001',
        as_of_date=date(2025, 2, 1),
    )


def test_build701n_found_result_preserves_only_verified_linked_input() -> None:
    record = _linked_record()

    result = InventoryAgeInputProviderResult(INPUT_FOUND, record, 'approved local read')

    assert result.outcome == INPUT_FOUND
    assert result.record is record
    assert result.reason == 'approved local read'
    assert result.is_found is True
    with pytest.raises(FrozenInstanceError):
        result.outcome = INPUT_UNAVAILABLE  # type: ignore[misc]


@pytest.mark.parametrize(
    'outcome',
    (INPUT_NOT_FOUND, INPUT_UNLINKED, INPUT_CONFLICTING, INPUT_UNAVAILABLE),
)
def test_build701n_nonfound_outcomes_carry_no_input_record(outcome: str) -> None:
    result = InventoryAgeInputProviderResult(outcome, reason='read boundary outcome')

    assert result.outcome == outcome
    assert result.record is None
    assert result.is_found is False


def test_build701n_result_rejects_unknown_or_nonfound_record_values() -> None:
    with pytest.raises(ValueError, match='unsupported'):
        InventoryAgeInputProviderResult('guessed')
    with pytest.raises(ValueError, match='only found'):
        InventoryAgeInputProviderResult(INPUT_UNLINKED, _linked_record())


def test_build701n_protocol_is_structural_and_read_only() -> None:
    class FixedProvider:
        def get_inventory_age_input(
            self,
            inventory_position_id: str,
            as_of_date: date,
        ) -> InventoryAgeInputProviderResult:
            assert inventory_position_id == 'asset-001'
            assert as_of_date == date(2025, 2, 1)
            return InventoryAgeInputProviderResult(INPUT_NOT_FOUND, reason='absent')

    provider = FixedProvider()

    assert isinstance(provider, InventoryAgeInputProvider)
    assert provider.get_inventory_age_input('asset-001', date(2025, 2, 1)).outcome == INPUT_NOT_FOUND


def test_build701n_provider_contract_has_no_persistence_or_network_dependency() -> None:
    source = Path('reports/inventory_age_provider.py').read_text(encoding='utf-8').lower()

    assert INVENTORY_AGE_INPUT_OUTCOMES == frozenset(
        {INPUT_FOUND, INPUT_NOT_FOUND, INPUT_UNLINKED, INPUT_CONFLICTING, INPUT_UNAVAILABLE}
    )
    assert 'sqlite' not in source
    assert 'repository' not in source
    assert 'requests' not in source
    assert 'http' not in source
