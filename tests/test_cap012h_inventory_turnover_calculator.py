from datetime import date
from decimal import Decimal

from reports.inventory_turnover_calculator import (
    EVIDENCE_AVAILABLE,
    EVIDENCE_CONFLICTING,
    EVIDENCE_UNAVAILABLE,
    DeterministicInventoryTurnoverProvider,
    InventoryTurnoverEvidence,
)
from reports.inventory_turnover_contract import (
    OUTCOME_CONFLICT,
    OUTCOME_NO_ELIGIBLE_INVENTORY,
    OUTCOME_UNAVAILABLE,
    OUTCOME_VALID,
    OUTCOME_ZERO_TURNOVER,
    InventoryTurnoverReportRequest,
)


def _request(*, group_by: str | None = None) -> InventoryTurnoverReportRequest:
    return InventoryTurnoverReportRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 2),
        source_coverage_required=('inventory', 'listing', 'audit'),
        group_by=group_by,
    )


def _evidence(
    opening: int | None,
    closing: int | None,
    completed: int | None,
    *,
    state: str = EVIDENCE_AVAILABLE,
    reason: str = 'approved fixture evidence',
) -> InventoryTurnoverEvidence:
    return InventoryTurnoverEvidence(
        opening_eligible_inventory_units=opening,
        closing_eligible_inventory_units=closing,
        completed_sale_units=completed,
        source_domains=('audit', 'inventory', 'listing'),
        source_coverage=('closed_period',),
        provenance=('fixture:opening', 'fixture:closing', 'fixture:completed-sales'),
        evidence_state=state,
        reason=reason,
    )


def test_calculates_valid_turnover_deterministically() -> None:
    provider = DeterministicInventoryTurnoverProvider(_evidence(10, 6, 4))

    result = provider.get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_VALID
    assert result.average_eligible_inventory_units == Decimal('8')
    assert result.turnover_ratio == Decimal('0.5')
    assert result.turnover_percentage == Decimal('50.0')
    assert result.completed_sale_units == 4


def test_calculates_zero_turnover_without_treating_it_as_unavailable() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(8, 8, 0)
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_ZERO_TURNOVER
    assert result.turnover_ratio == Decimal('0')
    assert result.turnover_percentage == Decimal('0')


def test_returns_no_inventory_for_zero_opening_closing_and_sales() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(0, 0, 0)
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_NO_ELIGIBLE_INVENTORY
    assert result.opening_eligible_inventory_units == 0
    assert result.closing_eligible_inventory_units == 0
    assert result.completed_sale_units == 0
    assert result.turnover_ratio is None
    assert result.turnover_percentage is None


def test_missing_quantity_evidence_fails_closed_without_numeric_values() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(None, 5, 2)
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_UNAVAILABLE
    assert result.turnover_ratio is None
    assert result.turnover_percentage is None


def test_conflicting_evidence_fails_closed_without_numeric_values() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(10, 6, 4, state=EVIDENCE_CONFLICTING, reason='quantity conflict')
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_CONFLICT
    assert result.reason == 'quantity conflict'
    assert result.turnover_ratio is None


def test_unavailable_evidence_fails_closed_without_numeric_values() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(None, None, None, state=EVIDENCE_UNAVAILABLE, reason='coverage missing')
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_UNAVAILABLE
    assert result.reason == 'coverage missing'
    assert result.completed_sale_units is None


def test_sales_with_zero_average_inventory_are_conflicting() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(0, 0, 1)
    ).get_inventory_turnover_result(_request())

    assert result.outcome == OUTCOME_CONFLICT
    assert result.turnover_ratio is None
    assert result.turnover_percentage is None


def test_grouped_requests_fail_closed_until_grouped_result_shape_is_authorized() -> None:
    result = DeterministicInventoryTurnoverProvider(
        _evidence(10, 6, 4)
    ).get_inventory_turnover_result(_request(group_by='product_id'))

    assert result.outcome == OUTCOME_UNAVAILABLE
    assert result.reason == 'grouped Inventory Turnover results are not authorized'
    assert result.turnover_ratio is None
