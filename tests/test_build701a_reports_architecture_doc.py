from pathlib import Path


DOC_PATH = Path('docs/Architecture/BUILD_701_REPORTS_FOUNDATION.md')


def test_build701_reports_architecture_doc_exists() -> None:
    assert DOC_PATH.exists()


def test_reports_architecture_preserves_source_domain_authority() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'CAP-012' in content
    assert 'Source domains own facts' in content
    assert 'Reports must not mutate, reinterpret, or become the authority' in content
    assert 'composition-owned report query service' in content


def test_reports_architecture_is_offline_and_deterministic() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'remain useful without network access' in content
    assert 'must be deterministic' in content
    assert 'Missing or unavailable source data must be shown explicitly' in content
    assert 'must not invent placeholder prices' in content


def test_build701a_remains_documentation_only() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'Build 701A is documentation-only' in content
    assert 'persistence-free Reports catalog' in content
    assert 'does not introduce:' in content
    assert 'report workspaces' in content
    assert 'schema changes' in content
    assert 'live providers' in content
