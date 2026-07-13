from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from reports.inventory_age import (
    EVIDENCE_AVAILABLE,
    EVIDENCE_INVALID,
    EVIDENCE_UNAVAILABLE,
)
from reports.inventory_age_source import (
    PURCHASE_DATE_FIELD,
    InventoryAgeSourceEvidence,
    adapt_inventory_detail_purchase_date,
    parse_inventory_purchase_date,
)


def test_blank_purchase_date_is_unavailable() -> None:
    evidence = parse_inventory_purchase_date('   ')

    assert evidence.evidence_state == EVIDENCE_UNAVAILABLE
    assert evidence.source_date is None
    assert evidence.raw_value == ''
    assert evidence.reason == 'purchase_date_missing'


def test_strict_iso_purchase_date_is_available() -> None:
    evidence = parse_inventory_purchase_date(' 2026-07-12 ')

    assert evidence.evidence_state == EVIDENCE_AVAILABLE
    assert evidence.source_date == date(2026, 7, 12)
    assert evidence.raw_value == '2026-07-12'
    assert evidence.reason == 'purchase_date_available'
    assert evidence.source_domain == 'inventory'
    assert evidence.source_field == PURCHASE_DATE_FIELD
    with pytest.raises(FrozenInstanceError):
        evidence.reason = 'changed'


@pytest.mark.parametrize(
    ('raw_value', 'reason'),
    (
        ('07/12/2026', 'purchase_date_invalid_iso'),
        ('2026-7-12', 'purchase_date_invalid_iso'),
        ('not-a-date', 'purchase_date_invalid_iso'),
        ('2026-02-30', 'purchase_date_invalid_calendar_date'),
    ),
)
def test_malformed_or_impossible_purchase_date_is_invalid(
    raw_value: str,
    reason: str,
) -> None:
    evidence = parse_inventory_purchase_date(raw_value)

    assert evidence.evidence_state == EVIDENCE_INVALID
    assert evidence.source_date is None
    assert evidence.raw_value == raw_value
    assert evidence.reason == reason


def test_adapter_reads_only_approved_purchase_date_field() -> None:
    evidence = adapt_inventory_detail_purchase_date(
        {
            'purchase_date': '2025-12-01',
            'created_at': '2024-01-01',
            'verified_at': '2026-07-12T00:00:00Z',
        }
    )
    missing = adapt_inventory_detail_purchase_date(
        {
            'created_at': '2024-01-01',
            'verified_at': '2026-07-12T00:00:00Z',
        }
    )

    assert evidence.source_date == date(2025, 12, 1)
    assert missing.evidence_state == EVIDENCE_UNAVAILABLE


def test_source_evidence_rejects_non_inventory_authority() -> None:
    with pytest.raises(ValueError, match='source_domain must remain inventory'):
        InventoryAgeSourceEvidence(
            EVIDENCE_AVAILABLE,
            date(2026, 7, 12),
            '2026-07-12',
            'available',
            source_domain='reports',
        )


def test_source_adapter_exposes_no_database_write_or_execution_behavior() -> None:
    evidence = parse_inventory_purchase_date('2026-07-12')

    assert not hasattr(evidence, 'save')
    assert not hasattr(evidence, 'execute')
    assert not hasattr(evidence, 'connect')
