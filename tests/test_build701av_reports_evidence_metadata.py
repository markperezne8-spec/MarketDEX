from composition.application_composition import ApplicationComposition


def test_build701av_composition_exposes_report_evidence_families(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    evidence_families = composition.report_evidence_families(
        ' INVENTORY-AGE-PATTERNS '
    )

    assert evidence_families == ('current_state', 'event_history')
    assert isinstance(evidence_families, tuple)
