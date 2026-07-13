from datetime import date
from pathlib import Path
from types import SimpleNamespace

from composition.application_composition import ApplicationComposition
from reports.inventory_age_query import INPUT_NOT_FOUND, InventoryAgeReportQueryResult
from reports.inventory_age_query_request import InventoryAgeReportQueryRequest
from reports.report_query_request import ReportQueryRequest


def test_build701ap_composition_routes_immutable_report_query_request() -> None:
    composition = ApplicationComposition(Path(':memory:'))
    expected = InventoryAgeReportQueryResult(INPUT_NOT_FOUND, reason='no approved evidence')
    requests = []

    def fake_query(request: ReportQueryRequest, **kwargs):
        requests.append(request)
        return expected

    composition.report_query = SimpleNamespace(query=fake_query)

    result = composition.query_report(
        ' INVENTORY-AGE-PATTERNS ',
        ' position-701ap ',
        date(2026, 7, 13),
    )

    assert result is expected
    assert requests == [
        ReportQueryRequest(
            'inventory-age-patterns',
            InventoryAgeReportQueryRequest('position-701ap', date(2026, 7, 13)),
        )
    ]
