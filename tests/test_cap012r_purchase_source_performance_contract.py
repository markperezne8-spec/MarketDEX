from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from reports.purchase_source_performance_contract import (
    OUTCOME_CONFLICT,
    OUTCOME_INVALID_REQUEST,
    OUTCOME_UNAVAILABLE,
    OUTCOME_VALID,
    OUTCOME_ZERO_SELL_THROUGH,
    PurchaseSourcePerformanceRequest,
    PurchaseSourcePerformanceResult,
    PurchaseSourcePerformanceResultCollection,
)


def request():
    return PurchaseSourcePerformanceRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 1),
        source_coverage_required=('inventory', 'confirmed_sales'),
    )


def result(outcome=OUTCOME_VALID, label='Target', sold=5, acquired=10):
    numeric = outcome in (OUTCOME_VALID, OUTCOME_ZERO_SELL_THROUGH)
    ratio = Decimal(sold) / Decimal(acquired) if numeric else None
    return PurchaseSourcePerformanceResult(
        request=request(),
        outcome=outcome,
        reason='contract evidence',
        source_domains=('inventory', 'sales'),
        source_coverage=('closed_period',),
        evidence_state='valid' if numeric else ('conflicting' if outcome == OUTCOME_CONFLICT else 'unavailable'),
        provenance=('inventory.purchase_source', 'sales.completed_quantity'),
        purchase_source_label=label if numeric else None,
        acquired_units=acquired if numeric else None,
        completed_sale_units=sold if numeric else None,
        remaining_unsold_units=acquired - sold if numeric else None,
        sell_through_ratio=ratio,
        sell_through_percentage=ratio * Decimal('100') if numeric else None,
    )


def test_request_is_immutable_and_deterministic():
    item = request()
    assert item.group_by == 'purchase_source'
    assert item.request_id == request().request_id
    with pytest.raises(FrozenInstanceError):
        item.scope = 'other'


def test_request_rejects_open_or_invalid_periods():
    with pytest.raises(ValueError, match='period_start'):
        PurchaseSourcePerformanceRequest(date(2026, 2, 1), date(2026, 2, 1), date(2026, 2, 1), ('inventory',))
    with pytest.raises(ValueError, match='as_of'):
        PurchaseSourcePerformanceRequest(date(2026, 1, 1), date(2026, 2, 1), date(2026, 1, 31), ('inventory',))


def test_exact_purchase_source_label_uses_trim_only_normalization():
    item = result(label='  Target Store  ')
    assert item.purchase_source_label == 'Target Store'


def test_valid_and_zero_sell_through_preserve_formula():
    valid = result()
    zero = result(outcome=OUTCOME_ZERO_SELL_THROUGH, sold=0)
    assert valid.sell_through_percentage == Decimal('50')
    assert valid.remaining_unsold_units == 5
    assert zero.sell_through_percentage == 0
    assert zero.remaining_unsold_units == 10


@pytest.mark.parametrize('outcome', [OUTCOME_UNAVAILABLE, OUTCOME_CONFLICT, OUTCOME_INVALID_REQUEST])
def test_fail_closed_outcomes_reject_numeric_values(outcome):
    with pytest.raises(ValueError, match='must not expose numeric values'):
        PurchaseSourcePerformanceResult(
            request=request(), outcome=outcome, reason='missing evidence',
            source_domains=('inventory',), source_coverage=('partial',),
            evidence_state='conflicting' if outcome == OUTCOME_CONFLICT else 'unavailable',
            provenance=('inventory.purchase_source',), acquired_units=1,
        )


def test_formula_mismatch_is_rejected():
    with pytest.raises(ValueError, match='approved formula'):
        PurchaseSourcePerformanceResult(
            request=request(), outcome=OUTCOME_VALID, reason='bad formula',
            source_domains=('inventory', 'sales'), source_coverage=('closed_period',),
            evidence_state='valid', provenance=('inventory.purchase_source',),
            purchase_source_label='Target', acquired_units=10, completed_sale_units=5,
            remaining_unsold_units=5, sell_through_ratio='0.4', sell_through_percentage='40',
        )


def test_collection_applies_deterministic_ordering():
    low = result(label='Walmart', sold=2)
    high = result(label='Target', sold=8)
    unavailable = result(outcome=OUTCOME_UNAVAILABLE)
    collection = PurchaseSourcePerformanceResultCollection(request(), (unavailable, low, high))
    assert [item.purchase_source_label for item in collection.results] == ['Target', 'Walmart', None]
