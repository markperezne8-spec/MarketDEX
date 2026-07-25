from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from reports.purchase_source_performance_calculator import (
    PurchaseSourcePerformanceEvidence,
    calculate_purchase_source_performance,
    calculate_purchase_source_performance_collection,
)
from reports.purchase_source_performance_contract import (
    OUTCOME_CONFLICT,
    OUTCOME_INVALID_REQUEST,
    OUTCOME_UNAVAILABLE,
    OUTCOME_VALID,
    OUTCOME_ZERO_SELL_THROUGH,
    PurchaseSourcePerformanceRequest,
)


def _request():
    return PurchaseSourcePerformanceRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 1),
        source_coverage_required=('inventory', 'completed_sales'),
    )


def _evidence(label='Local Shop', **overrides):
    values = dict(
        purchase_source_label=label,
        acquired_units=20,
        completed_sale_units=5,
        source_domains=('inventory', 'sales'),
        source_coverage=('inventory', 'completed_sales'),
        provenance=('inventory.purchase_source', 'sales.completed_units'),
    )
    values.update(overrides)
    return PurchaseSourcePerformanceEvidence(**values)


def test_evidence_is_frozen_and_preserves_trim_only_label():
    evidence = _evidence('  Local Shop  ')
    assert evidence.purchase_source_label == 'Local Shop'
    with pytest.raises(FrozenInstanceError):
        evidence.acquired_units = 99


def test_calculator_returns_valid_sell_through_result():
    result = calculate_purchase_source_performance(_request(), _evidence())
    assert result.outcome == OUTCOME_VALID
    assert result.acquired_units == 20
    assert result.completed_sale_units == 5
    assert result.remaining_unsold_units == 15
    assert result.sell_through_ratio == Decimal('0.25')
    assert result.sell_through_percentage == Decimal('25.00')


def test_calculator_returns_zero_sell_through():
    result = calculate_purchase_source_performance(
        _request(),
        _evidence(completed_sale_units=0),
    )
    assert result.outcome == OUTCOME_ZERO_SELL_THROUGH
    assert result.sell_through_percentage == 0
    assert result.remaining_unsold_units == 20


@pytest.mark.parametrize(
    ('evidence', 'outcome'),
    [
        (_evidence(acquired_units=None), OUTCOME_UNAVAILABLE),
        (_evidence(evidence_state='unavailable'), OUTCOME_UNAVAILABLE),
        (_evidence(evidence_state='conflicting'), OUTCOME_CONFLICT),
        (_evidence(acquired_units=0), OUTCOME_INVALID_REQUEST),
        (_evidence(completed_sale_units=21), OUTCOME_INVALID_REQUEST),
    ],
)
def test_calculator_fails_closed_without_numeric_output(evidence, outcome):
    result = calculate_purchase_source_performance(_request(), evidence)
    assert result.outcome == outcome
    assert result.sell_through_percentage is None
    assert result.sell_through_ratio is None


def test_collection_uses_contract_deterministic_ordering():
    collection = calculate_purchase_source_performance_collection(
        _request(),
        (
            _evidence('Beta', acquired_units=10, completed_sale_units=1),
            _evidence('Alpha', acquired_units=10, completed_sale_units=8),
            _evidence('Unavailable', evidence_state='unavailable'),
        ),
    )
    assert [item.purchase_source_label for item in collection.results] == [
        'Alpha',
        'Beta',
        'Unavailable',
    ]


def test_collection_rejects_non_tuple_evidence():
    with pytest.raises(TypeError):
        calculate_purchase_source_performance_collection(_request(), [])
