from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from reports.inventory_turnover_contract import (
    OUTCOME_CONFLICT,
    OUTCOME_NO_ELIGIBLE_INVENTORY,
    OUTCOME_VALID,
    InventoryTurnoverReportRequest,
    InventoryTurnoverReportResult,
)
from reports.inventory_turnover_presentation import (
    InventoryTurnoverPresentation,
    present_inventory_turnover,
)


def _request() -> InventoryTurnoverReportRequest:
    return InventoryTurnoverReportRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=date(2026, 2, 1),
        source_coverage_required=('inventory', 'listing', 'audit'),
    )


def test_valid_result_maps_to_deterministic_display_values() -> None:
    result = InventoryTurnoverReportResult(
        request=_request(),
        outcome=OUTCOME_VALID,
        reason='Complete evidence',
        source_domains=('inventory', 'listing', 'audit'),
        source_coverage=('complete',),
        evidence_state='available',
        provenance=('test',),
        opening_eligible_inventory_units=10,
        closing_eligible_inventory_units=6,
        average_eligible_inventory_units=Decimal('8'),
        completed_sale_units=4,
        turnover_ratio=Decimal('0.5'),
        turnover_percentage=Decimal('50'),
    )

    presentation = present_inventory_turnover(result)

    assert presentation == InventoryTurnoverPresentation(
        outcome='valid',
        status='VALID',
        reason='Complete evidence',
        period='2026-01-01 → 2026-02-01',
        formula='inventory-turnover-units-v1',
        evidence='available · complete',
        opening_units='10',
        closing_units='6',
        average_units='8',
        completed_sale_units='4',
        turnover_ratio='0.5×',
        turnover_percentage='50%',
    )


def test_conflict_result_exposes_no_numeric_values() -> None:
    result = InventoryTurnoverReportResult(
        request=_request(),
        outcome=OUTCOME_CONFLICT,
        reason='Contradictory evidence',
        source_domains=('inventory', 'listing', 'audit'),
        source_coverage=('conflicting',),
        evidence_state='conflict',
        provenance=('test',),
    )

    presentation = present_inventory_turnover(result)

    assert presentation.status == 'CONFLICT'
    assert presentation.reason == 'Contradictory evidence'
    assert {
        presentation.opening_units,
        presentation.closing_units,
        presentation.average_units,
        presentation.completed_sale_units,
        presentation.turnover_ratio,
        presentation.turnover_percentage,
    } == {'Unavailable'}


def test_no_eligible_inventory_preserves_zero_quantities_without_ratio() -> None:
    result = InventoryTurnoverReportResult(
        request=_request(),
        outcome=OUTCOME_NO_ELIGIBLE_INVENTORY,
        reason='No eligible business inventory',
        source_domains=('inventory', 'listing', 'audit'),
        source_coverage=('complete',),
        evidence_state='available',
        provenance=('test',),
        opening_eligible_inventory_units=0,
        closing_eligible_inventory_units=0,
        average_eligible_inventory_units=0,
        completed_sale_units=0,
    )

    presentation = present_inventory_turnover(result)

    assert presentation.opening_units == '0'
    assert presentation.closing_units == '0'
    assert presentation.average_units == '0'
    assert presentation.completed_sale_units == '0'
    assert presentation.turnover_ratio == 'Unavailable'
    assert presentation.turnover_percentage == 'Unavailable'


def test_presentation_is_immutable_and_rejects_wrong_input() -> None:
    result = InventoryTurnoverReportResult(
        request=_request(),
        outcome=OUTCOME_CONFLICT,
        reason='Conflict',
        source_domains=('inventory',),
        source_coverage=('conflicting',),
        evidence_state='conflict',
        provenance=('test',),
    )
    presentation = present_inventory_turnover(result)

    with pytest.raises(FrozenInstanceError):
        presentation.status = 'changed'  # type: ignore[misc]
    with pytest.raises(TypeError):
        present_inventory_turnover(object())  # type: ignore[arg-type]
