from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from reports.inventory_age_input import (
    PRODUCT_LINK_CONFLICTING,
    PRODUCT_LINK_LINKED,
    PRODUCT_LINK_UNLINKED,
    InventoryAgeInputRecord,
)


def _record(
    *,
    product_link_state: str = PRODUCT_LINK_LINKED,
    product_id: str | None = 'product-1',
) -> InventoryAgeInputRecord:
    return InventoryAgeInputRecord(
        inventory_position_id='asset-1',
        asset_name='Mega Evolution ETB',
        current_quantity=2,
        inventory_status='COMPLETED',
        purchase_date_raw=' 2026-07-01 ',
        storage_location=' Shelf A ',
        product_link_state=product_link_state,
        as_of_date=date(2026, 7, 12),
        product_id=product_id,
    )


def test_linked_record_preserves_separate_inventory_and_product_link_evidence() -> None:
    record = _record()

    assert record.inventory_position_id == 'asset-1'
    assert record.asset_name == 'Mega Evolution ETB'
    assert record.inventory_status == 'completed'
    assert record.purchase_date_raw == '2026-07-01'
    assert record.storage_location == 'Shelf A'
    assert record.product_link_state == PRODUCT_LINK_LINKED
    assert record.product_id == 'product-1'
    assert record.has_verified_product_link is True
    assert record.inventory_source_domain == 'inventory'
    assert record.product_link_authority == 'inventory_product_link'
    with pytest.raises(FrozenInstanceError):
        record.product_id = 'changed'


@pytest.mark.parametrize(
    'state',
    (
        PRODUCT_LINK_UNLINKED,
        PRODUCT_LINK_CONFLICTING,
    ),
)
def test_unlinked_or_conflicting_record_forbids_product_identity(state: str) -> None:
    record = _record(product_link_state=state, product_id=None)

    assert record.product_link_state == state
    assert record.product_id is None
    assert record.has_verified_product_link is False
    with pytest.raises(ValueError, match='must not contain product_id'):
        _record(product_link_state=state, product_id='product-1')


def test_linked_record_requires_canonical_product_id() -> None:
    with pytest.raises(ValueError, match='requires product_id'):
        _record(product_link_state=PRODUCT_LINK_LINKED, product_id=None)


def test_input_record_rejects_invalid_authority_or_quantity() -> None:
    with pytest.raises(ValueError, match='unsupported product_link_state'):
        _record(product_link_state='guessed', product_id=None)
    with pytest.raises(ValueError, match='non-negative integer'):
        InventoryAgeInputRecord(
            'asset-1',
            'Product',
            -1,
            'completed',
            '',
            '',
            PRODUCT_LINK_UNLINKED,
            date(2026, 7, 12),
        )
    with pytest.raises(ValueError, match='inventory_source_domain must remain inventory'):
        InventoryAgeInputRecord(
            'asset-1',
            'Product',
            1,
            'completed',
            '',
            '',
            PRODUCT_LINK_UNLINKED,
            date(2026, 7, 12),
            inventory_source_domain='reports',
        )


def test_input_record_has_no_database_or_execution_behavior() -> None:
    record = _record()

    assert not hasattr(record, 'save')
    assert not hasattr(record, 'execute')
    assert not hasattr(record, 'connect')
