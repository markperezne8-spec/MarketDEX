from datetime import date

from composition.application_composition import ApplicationComposition
from reports.inventory_age_query import INPUT_NOT_FOUND
from reports.report_query_service import ReportQueryService


def test_build701as_composition_routes_approved_report_query(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    assert isinstance(composition.report_query, ReportQueryService)

    result = composition.query_report(
        ' INVENTORY-AGE-PATTERNS ',
        'position-701as',
        date(2026, 7, 13),
    )

    assert result.outcome == INPUT_NOT_FOUND
