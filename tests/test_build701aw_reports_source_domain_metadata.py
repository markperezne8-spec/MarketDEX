from composition.application_composition import ApplicationComposition


def test_build701aw_composition_exposes_report_source_domains(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    source_domains = composition.report_source_domains(
        ' INVENTORY-AGE-PATTERNS '
    )

    assert source_domains == ('inventory',)
    assert isinstance(source_domains, tuple)
