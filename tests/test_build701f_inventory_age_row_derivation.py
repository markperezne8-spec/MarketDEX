from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from reports.inventory_age import (
    EVIDENCE_AVAILABLE,
    EVIDENCE_INVALID,
    EVIDENCE_UNAVAILABLE,
    InventoryAgeReportRow,
    derive_inventory_age_row,
    sort_inventory_age_rows,
)


def _derive(
    position_id: str,
    product_name: str,
    source_start_date: date | None,
    *,
    as_of_date: date = date(2026, 7, 12),
) -> InventoryAgeReportRow:
    return derive_inventory_age_row(
        inventory_position_id=position_id,
        product_id=f'product-{position_id}',
        product_name=product_name,
        current_quantity=1,
        inventory_status='OWNED',
        as_of_date=as_of_date,
        source_start_date=source_start_date,
        storage_location='Shelf A',
    )


def test_available_age_is_derived_from_explicit_dates() -> None:
    row = _derive('inv-1', 'Charizard ex', date(2026, 7, 1))

    assert row.age_days == 11
    assert row.evidence_state == EVIDENCE_AVAILABLE
    assert row.as_of_date == date(2026, 7, 12)
    assert row.source_start_date == date(2026, 7, 1)
    assert row.source_domain == 'inventory'
    assert row.inventory_status == 'owned'
    with pytest.raises(FrozenInstanceError):
        row.age_days = 12


def test_missing_start_date_is_unavailable_not_zero() -> None:
    row = _derive('inv-2', 'Mega Evolution ETB', None)

    assert row.evidence_state == EVIDENCE_UNAVAILABLE
    assert row.source_start_date is None
    assert row.age_days is None


def test_future_start_date_is_invalid_and_fails_closed() -> None:
    row = _derive('inv-3', 'Booster Pack', date(2026, 7, 13))

    assert row.evidence_state == EVIDENCE_INVALID
    assert row.source_start_date == date(2026, 7, 13)
    assert row.age_days is None


def test_row_rejects_inconsistent_or_non_inventory_authority() -> None:
    with pytest.raises(ValueError, match='must match the explicit dates'):
        InventoryAgeReportRow(
            'inv-1',
            'product-1',
            'Product',
            1,
            'owned',
            date(2026, 7, 12),
            date(2026, 7, 1),
            99,
            EVIDENCE_AVAILABLE,
        )
    with pytest.raises(ValueError, match='Inventory source authority'):
        InventoryAgeReportRow(
            'inv-1',
            'product-1',
            'Product',
            1,
            'owned',
            date(2026, 7, 12),
            date(2026, 7, 1),
            11,
            EVIDENCE_AVAILABLE,
            source_domain='listing',
        )
    with pytest.raises(ValueError, match='non-negative integer'):
        _derive_with_quantity(-1)


def _derive_with_quantity(quantity: int) -> InventoryAgeReportRow:
    return derive_inventory_age_row(
        inventory_position_id='inv-q',
        product_id='product-q',
        product_name='Quantity Product',
        current_quantity=quantity,
        inventory_status='owned',
        as_of_date=date(2026, 7, 12),
        source_start_date=date(2026, 7, 1),
    )


def test_sorting_is_explicit_and_deterministic() -> None:
    invalid = _derive('inv-invalid', 'Zulu', date(2026, 7, 13))
    unavailable = _derive('inv-unavailable', 'Alpha', None)
    older_b = _derive('inv-b', 'Beta', date(2026, 6, 1))
    older_a = _derive('inv-a', 'Alpha', date(2026, 6, 1))
    newer = _derive('inv-new', 'Gamma', date(2026, 7, 10))

    ordered = sort_inventory_age_rows((newer, older_b, unavailable, older_a, invalid))

    assert tuple(row.inventory_position_id for row in ordered) == (
        'inv-invalid',
        'inv-unavailable',
        'inv-a',
        'inv-b',
        'inv-new',
    )


def test_derivation_exposes_no_wall_clock_persistence_or_execution() -> None:
    row = _derive('inv-4', 'Offline Product', date(2026, 7, 2))

    assert not hasattr(row, 'save')
    assert not hasattr(row, 'execute')
    assert not hasattr(row, 'export')
