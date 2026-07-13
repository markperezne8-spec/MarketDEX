from composition.application_composition import ApplicationComposition


def test_build701ax_composition_exposes_report_description(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    description = composition.report_description(' INVENTORY-AGE-PATTERNS ')

    assert description.startswith('Workbook-backed definition')
    assert description.endswith('thresholds.')
