from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from reports.inventory_turnover_contract import (
    BUSINESS_INVENTORY_SCOPE,
    GROUP_BY_PRODUCT_CATEGORY,
    INVENTORY_TURNOVER_FORMULA_ID,
    INVENTORY_TURNOVER_REPORT_ID,
    OUTCOME_CONFLICT,
    OUTCOME_INVALID_REQUEST,
    OUTCOME_NO_ELIGIBLE_INVENTORY,
    OUTCOME_UNAVAILABLE,
    OUTCOME_VALID,
    OUTCOME_ZERO_TURNOVER,
    InventoryTurnoverReportRequest,
    InventoryTurnoverReportResult,
)


def _request(group_by: str | None = None) -> InventoryTurnoverReportRequest:
    return InventoryTurnoverReportRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 2),
        source_coverage_required=('Inventory', 'Completed Sale', 'inventory'),
        group_by=group_by,
    )


def _result(
    outcome: str = OUTCOME_VALID,
    **overrides: object,
) -> InventoryTurnoverReportResult:
    values: dict[str, object] = {
        'request': _request(),
        'outcome': outcome,
        'reason': 'contract evidence is available',
        'source_domains': ('Inventory', 'Completed Sale', 'inventory'),
        'source_coverage': ('closed_period', 'source fields available'),
        'evidence_state': 'available',
        'provenance': ('inventory.quantity', 'completed_sale.quantity'),
        'opening_eligible_inventory_units': 10,
        'closing_eligible_inventory_units': 6,
        'average_eligible_inventory_units': Decimal('8'),
        'completed_sale_units': 2,
        'turnover_ratio': Decimal('0.25'),
        'turnover_percentage': Decimal('25'),
    }
    values.update(overrides)
    return InventoryTurnoverReportResult(**values)


def test_cap012e_request_normalizes_identity_and_remains_immutable() -> None:
    request = InventoryTurnoverReportRequest(
        report_id='  inventory turnover  ',
        formula_id=' inventory_turnover_units_v1 ',
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        scope=' Business Inventory ',
        group_by=' Product Category ',
        as_of=date(2026, 2, 2),
        source_coverage_required=('Inventory', 'Completed Sale', 'inventory'),
        include_in_progress_period=1,
    )

    assert request.report_id == INVENTORY_TURNOVER_REPORT_ID
    assert request.formula_id == INVENTORY_TURNOVER_FORMULA_ID
    assert request.scope == BUSINESS_INVENTORY_SCOPE
    assert request.group_by == GROUP_BY_PRODUCT_CATEGORY
    assert request.include_in_progress_period is True
    assert request.source_coverage_required == ('completed_sale', 'inventory')
    assert request.request_id == (
        'inventory-turnover|inventory-turnover-units-v1|2026-01-01|2026-02-01|'
        'business_inventory|product_category|2026-02-02|completed_sale,inventory|'
        'in_progress'
    )
    with pytest.raises((AttributeError, FrozenInstanceError)):
        request.scope = 'changed'


@pytest.mark.parametrize(
    ('kwargs', 'message'),
    [
        ({'formula_id': 'invented-formula'}, 'formula_id must be inventory-turnover-units-v1'),
        ({'report_id': 'invented-report'}, 'report_id must be inventory-turnover'),
        ({'period_end': date(2026, 1, 1)}, 'period_start must be before period_end'),
        ({'scope': 'collection'}, 'scope must be business_inventory'),
        ({'group_by': 'unknown'}, 'unsupported group_by'),
        ({'source_coverage_required': ()}, 'at least one source_coverage_required'),
    ],
)
def test_cap012e_request_rejects_invalid_contract_shape(
    kwargs: dict[str, object],
    message: str,
) -> None:
    values: dict[str, object] = {
        'period_start': date(2026, 1, 1),
        'period_end': date(2026, 2, 1),
        'as_of': date(2026, 2, 2),
        'source_coverage_required': ('inventory',),
    }
    values.update(kwargs)

    with pytest.raises(ValueError, match=message):
        InventoryTurnoverReportRequest(**values)


def test_cap012e_request_requires_explicit_dates_and_iterable_coverage() -> None:
    with pytest.raises(TypeError, match='period_start must be a date'):
        InventoryTurnoverReportRequest(
            period_start='2026-01-01',
            period_end=date(2026, 2, 1),
            as_of=date(2026, 2, 2),
            source_coverage_required=('inventory',),
        )

    with pytest.raises(TypeError, match='source_coverage_required must be an iterable'):
        InventoryTurnoverReportRequest(
            period_start=date(2026, 1, 1),
            period_end=date(2026, 2, 1),
            as_of=date(2026, 2, 2),
            source_coverage_required='inventory',
        )


def test_cap012e_valid_result_preserves_contract_fields_and_immutability() -> None:
    result = _result(group_key=' Product A ', group_label=' Product A ')

    assert result.report_id == INVENTORY_TURNOVER_REPORT_ID
    assert result.formula_id == INVENTORY_TURNOVER_FORMULA_ID
    assert result.period_start == date(2026, 1, 1)
    assert result.period_end == date(2026, 2, 1)
    assert result.scope == BUSINESS_INVENTORY_SCOPE
    assert result.as_of == date(2026, 2, 2)
    assert result.group_key == 'product_a'
    assert result.group_label == 'Product A'
    assert result.source_domains == ('completed_sale', 'inventory')
    assert result.source_coverage == ('closed_period', 'source_fields_available')
    assert result.evidence_state == 'available'
    assert result.provenance == ('inventory.quantity', 'completed_sale.quantity')
    assert result.opening_eligible_inventory_units == 10
    assert result.closing_eligible_inventory_units == 6
    assert result.average_eligible_inventory_units == Decimal('8')
    assert result.completed_sale_units == 2
    assert result.turnover_ratio == Decimal('0.25')
    assert result.turnover_percentage == Decimal('25')
    with pytest.raises((AttributeError, FrozenInstanceError)):
        result.reason = 'changed'


def test_cap012e_zero_and_no_inventory_outcomes_are_distinct() -> None:
    zero = _result(
        OUTCOME_ZERO_TURNOVER,
        completed_sale_units=0,
        turnover_ratio=Decimal('0'),
        turnover_percentage=Decimal('0'),
    )
    assert zero.outcome == OUTCOME_ZERO_TURNOVER
    assert zero.average_eligible_inventory_units == Decimal('8')

    no_inventory = _result(
        OUTCOME_NO_ELIGIBLE_INVENTORY,
        opening_eligible_inventory_units=0,
        closing_eligible_inventory_units=0,
        average_eligible_inventory_units=Decimal('0'),
        completed_sale_units=0,
        turnover_ratio=None,
        turnover_percentage=None,
    )
    assert no_inventory.outcome == OUTCOME_NO_ELIGIBLE_INVENTORY
    assert no_inventory.turnover_ratio is None
    assert no_inventory.turnover_percentage is None


def test_cap012e_unavailable_conflict_and_invalid_request_fail_closed() -> None:
    for outcome in (OUTCOME_UNAVAILABLE, OUTCOME_CONFLICT, OUTCOME_INVALID_REQUEST):
        result = _result(
            outcome,
            opening_eligible_inventory_units=None,
            closing_eligible_inventory_units=None,
            average_eligible_inventory_units=None,
            completed_sale_units=None,
            turnover_ratio=None,
            turnover_percentage=None,
        )
        assert result.outcome == outcome

    with pytest.raises(ValueError, match='unavailable outcome must not expose numeric fields'):
        _result(
            OUTCOME_UNAVAILABLE,
            opening_eligible_inventory_units=10,
            closing_eligible_inventory_units=None,
            average_eligible_inventory_units=None,
            completed_sale_units=None,
            turnover_ratio=None,
            turnover_percentage=None,
        )


@pytest.mark.parametrize(
    ('outcome', 'overrides', 'message'),
    [
        (
            OUTCOME_VALID,
            {'completed_sale_units': 0},
            'valid outcome requires completed sale units greater than zero',
        ),
        (
            OUTCOME_VALID,
            {'turnover_ratio': Decimal('0')},
            'valid outcome requires positive turnover values',
        ),
        (
            OUTCOME_ZERO_TURNOVER,
            {'completed_sale_units': 1, 'turnover_ratio': Decimal('0')},
            'zero turnover requires completed sale units equal zero',
        ),
        (
            OUTCOME_NO_ELIGIBLE_INVENTORY,
            {
                'opening_eligible_inventory_units': 0,
                'closing_eligible_inventory_units': 0,
                'average_eligible_inventory_units': Decimal('0'),
                'completed_sale_units': 0,
                'turnover_ratio': Decimal('0'),
                'turnover_percentage': Decimal('0'),
            },
            'no eligible inventory must not expose turnover values',
        ),
    ],
)
def test_cap012e_result_rejects_contradictory_outcome_fields(
    outcome: str,
    overrides: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        _result(outcome, **overrides)


def test_cap012e_grouped_results_have_deterministic_sort_keys() -> None:
    request = _request(group_by=GROUP_BY_PRODUCT_CATEGORY)
    beta = _result(request=request, group_key='beta', group_label='Beta')
    alpha = _result(request=request, group_key='alpha', group_label='Alpha')

    assert [result.group_key for result in sorted((beta, alpha), key=lambda item: item.sort_key)] == [
        'alpha',
        'beta',
    ]
