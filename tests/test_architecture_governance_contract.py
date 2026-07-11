from pathlib import Path


def test_architecture_gate_framework_is_repository_authority():
    text = Path('docs/governance/Architecture_Gates.md').read_text(encoding='utf-8')

    for gate in (
        'Authority gate',
        'Architecture gate',
        'Behavior gate',
        'Data gate',
        'UX gate',
        'Integration gate',
        'Packaging gate',
        'Release gate',
    ):
        assert gate in text

    assert 'Every material pull request must record' in text
    assert 'No second launcher, shell, database authority' in text


def test_ec005_records_current_stacked_history_and_exact_resume_point():
    text = Path(
        'docs/checkpoints/EC-005_Shell_Composition_Market_Intelligence.md'
    ).read_text(encoding='utf-8')

    for pull_request in ('PR #163', 'PR #164', 'PR #165', 'PR #166'):
        assert pull_request in text

    assert 'Mandatory checkpoint results' in text
    assert 'Exact resume point' in text
    assert 'Collection Overview Workspace' in text
