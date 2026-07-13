from datetime import date

import pytest

from reports.inventory_age import (
    EVIDENCE_AVAILABLE,
    EVIDENCE_INVALID,
    EVIDENCE_UNAVAILABLE,
)
from reports.inventory_age_bridge import build_inventory_age_row_from_input
from reports.inventory_age_input import (
    PRODUCT_LINK_CONFLICTING,
    PRODUCT_LINK_LINKED,
    PRODUCT_LINK_UNLINKED,
    InventoryAgeInputRecord,
)


def _record(
    *,
    purchase_date_raw: str,
    link_state: str = PRODUCT_LINK_LINKED,
    product_id: str | None = 'product-1',
) -> InventoryAgeInputRecord:
    return InventoryAgeInputRecord(
        inventory_position_id='asset-1',
        asset_name='Mega Evolution ETB',
        current_quantity=2,
        inventory_status='completed',
        purchase_date_raw=purchase_date_raw,
        storage_location='Shelf A',
        product_link_state=link_state,
        as_of_date=date(2026, 7, 12),
        product_id=product_id,
    )


def test_bridge_builds_available_row_from_linked_iso_evidence() -> None:
    row = build_inventory_age_row_from_input(
        _record(purchase_date_raw='2026-07-01')
    )

    assert row.product_id == 'product-1'
    assert row.evidence_state == EVIDENCE_AVAILABLE
    assert row.age_days == 11
    assert row.source_date_raw == '2026-07-01'


def test_bridge_preserves_unavailable_and_malformed_evidence() -> None:
    unavailable = build_inventory_age_row_from_input(_record(purchase_date_raw=''))
    invalid = build_inventory_age_row_from_input(
        _record(purchase_date_raw='07/01/2026')
    )

    assert (unavailable.evidence_state, unavailable.age_days) == (
        EVIDENCE_UNAVAILABLE,
        None,
    )
    assert (invalid.evidence_state, invalid.age_days, invalid.source_date_raw) == (
        EVIDENCE_INVALID,
        None,
        '07/01/2026',
    )
    assert invalid.evidence_reason == 'purchase_date_invalid_iso'


def test_bridge_preserves_future_date_as_invalid() -> None:
    row = build_inventory_age_row_from_input(
        _record(purchase_date_raw='2026-07-13')
    )

    assert row.evidence_state == EVIDENCE_INVALID
    assert row.source_date_raw == '2026-07-13'
    assert row.evidence_reason == 'source_date_after_as_of'


@pytest.mark.parametrize(
    ('link_state', 'product_id'),
    (
        (PRODUCT_LINK_UNLINKED, None),
        (PRODUCT_LINK_CONFLICTING, None),
    ),
)
def test_bridge_fails_closed_without_verified_product_link(
    link_state: str,
    product_id: str | None,
) -> None:
    with pytest.raises(ValueError, match='requires verified product-link evidence'):
        build_inventory_age_row_from_input(
            _record(
                purchase_date_raw='2026-07-01',
                link_state=link_state,
                product_id=product_id,
            )
        )


def test_bridge_has_no_database_or_execution_behavior() -> None:
    row = build_inventory_age_row_from_input(_record(purchase_date_raw='2026-07-01'))

    assert not hasattr(row, 'save')
    assert not hasattr(row, 'execute')
    assert not hasattr(row, 'connect')
