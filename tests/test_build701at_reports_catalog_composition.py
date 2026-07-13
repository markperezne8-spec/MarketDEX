from composition.application_composition import ApplicationComposition
from reports.definitions import ReportDefinition


def test_build701at_composition_exposes_immutable_report_catalog(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    reports = composition.list_reports()

    assert isinstance(reports, tuple)
    assert len(reports) == 1
    assert isinstance(reports[0], ReportDefinition)
    assert reports[0].report_id == 'inventory-age-patterns'
    assert reports[0].name == 'Inventory Age Patterns'
