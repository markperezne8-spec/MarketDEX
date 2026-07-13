from datetime import date
from pathlib import Path
from types import SimpleNamespace

from composition.application_composition import ApplicationComposition
from reports.inventory_age_query import INPUT_NOT_FOUND, InventoryAgeReportQueryResult
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest


def test_build701ah_composition_constructs_validated_query_request() -> None:
    composition = ApplicationComposition(Path(':memory:'))
    expected = InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no approved evidence')
    requests = []

    def fake_query(request: InventoryAgeReportQueryRequest):
        requests.append(request)
        return expected

    composition.inventory_age_report_query = SimpleNamespace(
        get_inventory_age_for_request=fake_query
    )

    result = composition.query_inventory_age('  position-701ah  ', date(2026, 7, 13))

    assert result is expected
    assert requests == [
        InventoryAgeReportQueryRequest('position-701ah', date(2026, 7, 13))
    ]
