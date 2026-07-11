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
        'Platform compatibility gate',
        'AI safety gate',
        'Packaging gate',
        'Release gate',
    ):
        assert gate in text

    assert 'Every material pull request must record' in text
    assert 'No second launcher, shell, database authority' in text
    assert 'No active mobile or web application tree' in text
    assert 'No direct AI mutation of SQLite' in text


def test_platform_strategy_is_desktop_first_and_future_compatible():
    text = Path('docs/governance/Platform_Strategy.md').read_text(encoding='utf-8')

    assert 'Windows desktop application first' in text
    assert 'No iOS, Android, or browser application is currently in scope' in text
    assert 'must not depend on PySide6 widgets' in text
    assert 'Funko Pops' in text
    assert 'controlled commands and read models' in text


def test_approved_architecture_roadmap_records_product_owner_authority():
    text = Path('docs/governance/Approved_Architecture_Roadmap.md').read_text(
        encoding='utf-8'
    )

    assert 'Product Owner approved' in text
    assert 'Pokémon TCG' in text
    assert 'future iOS, Android, and web compatibility' in text
    assert 'Canonical shell and workspace authority' in text
    assert 'Architecture enforcement in CI' in text
    assert 'does not authorize destructive data changes' in text


def test_ec005_records_current_stacked_history_and_exact_resume_point():
    text = Path(
        'docs/checkpoints/EC-005_Shell_Composition_Market_Intelligence.md'
    ).read_text(encoding='utf-8')

    for pull_request in ('PR #163', 'PR #164', 'PR #165', 'PR #166'):
        assert pull_request in text

    assert 'Mandatory checkpoint results' in text
    assert 'Platform compatibility' in text
    assert 'AI safety' in text
    assert 'Exact resume point' in text
    assert 'Collection Overview Workspace' in text
