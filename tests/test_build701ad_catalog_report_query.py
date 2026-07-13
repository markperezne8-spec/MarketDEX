from datetime import date
from pathlib import Path

import pytest

from composition.application_composition import ApplicationComposition
from reports.inventory_age_query import INPUT_NOT_FOUND, InventoryAgeReportQueryResult


def test_build701ad_catalog_report_query_routes_inventory_age() -> None:
    composition = ApplicationComposition(Path(':memory:'))
    expected = InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no approved evidence')
    calls = []

    def fake_query(position_id: str, as_of: date) -> InventoryAgeReportQueryResult:
        calls.append((position_id, as_of))
        return expected

    composition.query_inventory_age = fake_query
    requested_date = date(2026, 7, 13)

    result = composition.query_report(
        'inventory-age-patterns',
        'position-701ad',
        requested_date,
    )

    assert result is expected
    assert calls == [('position-701ad', requested_date)]


def test_build701ad_catalog_report_query_rejects_unknown_report() -> None:
    composition = ApplicationComposition(Path(':memory:'))

    with pytest.raises(KeyError, match='unknown report'):
        composition.query_report(
            'unknown-report',
            'position-701ad',
            date(2026, 7, 13),
        )


def test_build701ad_catalog_report_query_is_not_invoked_during_startup() -> None:
    source = Path('composition/application_composition.py').read_text(encoding='utf-8')
    runtime_source = source.split('    def verify_runtime', 1)[1]

    assert 'self.query_report(' not in runtime_source
    assert 'def query_report(' in source
