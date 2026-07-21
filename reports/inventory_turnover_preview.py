from __future__ import annotations

from datetime import date
from decimal import Decimal

from reports.inventory_turnover_contract import (
    InventoryTurnoverReportRequest,
    InventoryTurnoverReportResult,
)


def build_inventory_turnover_preview_result() -> InventoryTurnoverReportResult:
    """Return the canonical deterministic read-only Inventory Turnover preview."""

    return InventoryTurnoverReportResult(
        request=InventoryTurnoverReportRequest(
            period_start=date(2026, 1, 1),
            period_end=date(2026, 2, 1),
            as_of=date(2026, 2, 1),
            source_coverage_required=('closed_period',),
        ),
        outcome='valid',
        reason='Deterministic read-only sample',
        source_domains=('inventory', 'listing', 'audit'),
        source_coverage=('closed_period',),
        evidence_state='available',
        provenance=('reports:deterministic-preview',),
        opening_eligible_inventory_units=10,
        closing_eligible_inventory_units=6,
        average_eligible_inventory_units=Decimal('8'),
        completed_sale_units=4,
        turnover_ratio=Decimal('0.5'),
        turnover_percentage=Decimal('50'),
    )
