from datetime import date

import pytest

from reports.inventory_age import (
    EVIDENCE_AVAILABLE,
    EVIDENCE_INVALID,
    EVIDENCE_UNAVAILABLE,
    InventoryAgeReportRow,
    derive_inventory_age_row,
)


def _row(
    *,
    evidence_state: str,
    source_start_date: date | None,
    age_days: int | None,
    source_date_raw: str = '',
    evidence_reason: str = '',
) -> InventoryAgeReportRow:
    return InventoryAgeReportRow(
        inventory_position_id='inv-1',
        product_id='product-1',
        product_name='Inventory Product',
        current_quantity=1,
        inventory_status='owned',
        as_of_date=date(2026, 7, 12),
        source_start_date=source_start_date,
        age_days=age_days,
        evidence_state=evidence_state,
        source_date_raw=source_date_raw,
        evidence_reason=evidence_reason,
    )


def test_available_row_normalizes_raw_value_and_reason() -> None:
    row = _row(
        evidence_state=EVIDENCE_AVAILABLE,
        source_start_date=date(2026, 7, 1),
        age_days=11,
    )

    assert row.source_date_raw == '2026-07-01'
    assert row.evidence_reason == 'source_date_available'


def test_unavailable_row_preserves_missing_reason_without_false_date() -> None:
    row = _row(
        evidence_state=EVIDENCE_UNAVAILABLE,
        source_start_date=None,
        age_days=None,
    )

    assert row.source_date_raw == ''
    assert row.evidence_reason == 'source_date_missing'


def test_invalid_row_preserves_malformed_raw_evidence() -> None:
    row = _row(
        evidence_state=EVIDENCE_INVALID,
        source_start_date=None,
        age_days=None,
        source_date_raw=' 07/12/2026 ',
        evidence_reason='purchase_date_invalid_iso',
    )

    assert row.source_date_raw == '07/12/2026'
    assert row.evidence_reason == 'purchase_date_invalid_iso'
    assert row.age_days is None


def test_invalid_future_date_preserves_normalized_date_and_reason() -> None:
    row = _row(
        evidence_state=EVIDENCE_INVALID,
        source_start_date=date(2026, 7, 13),
        age_days=None,
    )

    assert row.source_date_raw == '2026-07-13'
    assert row.evidence_reason == 'source_date_after_as_of'


def test_invalid_row_rejects_empty_or_ambiguous_evidence() -> None:
    with pytest.raises(ValueError, match='invalid evidence requires'):
        _row(
            evidence_state=EVIDENCE_INVALID,
            source_start_date=None,
            age_days=None,
        )
    with pytest.raises(ValueError, match='must not contain age_days'):
        _row(
            evidence_state=EVIDENCE_INVALID,
            source_start_date=None,
            age_days=0,
            source_date_raw='not-a-date',
        )


def test_existing_derivation_retains_available_and_unavailable_contracts() -> None:
    available = derive_inventory_age_row(
        inventory_position_id='inv-available',
        product_id='product-available',
        product_name='Available',
        current_quantity=1,
        inventory_status='owned',
        as_of_date=date(2026, 7, 12),
        source_start_date=date(2026, 7, 1),
    )
    unavailable = derive_inventory_age_row(
        inventory_position_id='inv-unavailable',
        product_id='product-unavailable',
        product_name='Unavailable',
        current_quantity=1,
        inventory_status='owned',
        as_of_date=date(2026, 7, 12),
        source_start_date=None,
    )

    assert (available.evidence_state, available.source_date_raw) == (
        EVIDENCE_AVAILABLE,
        '2026-07-01',
    )
    assert (unavailable.evidence_state, unavailable.source_date_raw) == (
        EVIDENCE_UNAVAILABLE,
        '',
    )
