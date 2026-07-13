from datetime import date
from pathlib import Path
from types import SimpleNamespace

from composition.application_composition import ApplicationComposition
from reports.inventory_age_query import (
    INPUT_NOT_FOUND,
    InventoryAgeReportQueryResult,
)
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest


def test_build701ab_composition_forwards_inventory_age_query() -> None:
    composition = ApplicationComposition(Path(':memory:'))
    calls = []
    expected = InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no approved evidence')

    def fake_query(request: InventoryAgeReportQueryRequest) -> InventoryAgeReportQueryResult:
        calls.append((request.inventory_position_id, request.as_of_date))
        return expected

    composition.inventory_age_report_query = SimpleNamespace(
        get_inventory_age_for_request=fake_query
    )
    requested_date = date(2026, 7, 13)

    result = composition.query_inventory_age('position-701ab', requested_date)

    assert result is expected
    assert calls == [('position-701ab', requested_date)]


def test_build701ab_query_boundary_is_not_invoked_during_startup() -> None:
    source = Path('composition/application_composition.py').read_text(encoding='utf-8')
    runtime_source = source.split('    def verify_runtime', 1)[1]

    assert 'self.query_inventory_age(' not in runtime_source
    assert 'self.inventory_age_report_query.get_inventory_age_row(' not in runtime_source
    assert 'def query_inventory_age(' in source
