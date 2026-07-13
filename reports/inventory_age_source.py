from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import Mapping

from reports.inventory_age import (
    EVIDENCE_AVAILABLE,
    EVIDENCE_INVALID,
    EVIDENCE_UNAVAILABLE,
)


ISO_DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
PURCHASE_DATE_FIELD = 'purchase_date'


@dataclass(frozen=True, slots=True)
class InventoryAgeSourceEvidence:
    """Parsed read-only evidence from an Inventory-owned purchase date."""

    evidence_state: str
    source_date: date | None
    raw_value: str
    reason: str
    source_domain: str = 'inventory'
    source_field: str = PURCHASE_DATE_FIELD

    def __post_init__(self) -> None:
        if self.evidence_state not in {
            EVIDENCE_AVAILABLE,
            EVIDENCE_UNAVAILABLE,
            EVIDENCE_INVALID,
        }:
            raise ValueError(f'unsupported evidence_state: {self.evidence_state}')
        if self.source_domain != 'inventory':
            raise ValueError('source_domain must remain inventory')
        if self.source_field != PURCHASE_DATE_FIELD:
            raise ValueError('source_field must remain purchase_date')
        if self.evidence_state == EVIDENCE_AVAILABLE and self.source_date is None:
            raise ValueError('available evidence requires source_date')
        if self.evidence_state != EVIDENCE_AVAILABLE and self.source_date is not None:
            raise ValueError('unavailable or invalid evidence must not contain source_date')
        if not self.reason.strip():
            raise ValueError('reason is required')
        object.__setattr__(self, 'raw_value', self.raw_value.strip())
        object.__setattr__(self, 'reason', self.reason.strip())


def parse_inventory_purchase_date(value: object) -> InventoryAgeSourceEvidence:
    """Parse strict date-only Inventory evidence without persistence access."""

    raw_value = str(value or '').strip()
    if not raw_value:
        return InventoryAgeSourceEvidence(
            evidence_state=EVIDENCE_UNAVAILABLE,
            source_date=None,
            raw_value='',
            reason='purchase_date_missing',
        )

    if not ISO_DATE_PATTERN.fullmatch(raw_value):
        return InventoryAgeSourceEvidence(
            evidence_state=EVIDENCE_INVALID,
            source_date=None,
            raw_value=raw_value,
            reason='purchase_date_invalid_iso',
        )

    try:
        source_date = date.fromisoformat(raw_value)
    except ValueError:
        return InventoryAgeSourceEvidence(
            evidence_state=EVIDENCE_INVALID,
            source_date=None,
            raw_value=raw_value,
            reason='purchase_date_invalid_calendar_date',
        )

    return InventoryAgeSourceEvidence(
        evidence_state=EVIDENCE_AVAILABLE,
        source_date=source_date,
        raw_value=raw_value,
        reason='purchase_date_available',
    )


def adapt_inventory_detail_purchase_date(
    detail: Mapping[str, object],
) -> InventoryAgeSourceEvidence:
    """Adapt only the approved Inventory detail field into source evidence."""

    return parse_inventory_purchase_date(detail.get(PURCHASE_DATE_FIELD))
