import pytest

from composition.application_composition import ApplicationComposition


def test_build701au_composition_resolves_approved_report_definition(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    report = composition.get_report_definition(' INVENTORY-AGE-PATTERNS ')

    assert report is composition.list_reports()[0]
    assert report.report_id == 'inventory-age-patterns'
    assert report.name == 'Inventory Age Patterns'


def test_build701au_composition_rejects_unknown_report_definition(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    with pytest.raises(KeyError, match='unknown report'):
        composition.get_report_definition('not-a-report')
