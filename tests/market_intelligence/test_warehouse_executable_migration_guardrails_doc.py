from pathlib import Path


DOC_PATH = Path('docs/market_intelligence/warehouse_executable_migration_guardrails.md')


def test_executable_migration_guardrails_doc_exists() -> None:
    assert DOC_PATH.exists()


def test_executable_migration_guardrails_require_safe_preflight_and_dry_run() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'Required preflight checks' in content
    assert 'dry-run validation succeeds before execution mode is allowed' in content
    assert 'fail closed before performing writes' in content
    assert 'Dry-run output must be deterministic' in content


def test_executable_migration_guardrails_preserve_offline_boundaries() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'offline mode without network access' in content
    assert 'Product Registry remains the authority for product identity' in content
    assert 'Repository interfaces remain the boundary' in content
    assert 'no live provider, scraper, API credential, scheduler, alert, or cloud-sync dependency is required' in content


def test_executable_migration_guardrails_remain_planning_only() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    assert 'does not introduce:' in content
    assert 'SQL files' in content
    assert 'executable migrations' in content
    assert 'SQLite connections' in content
    assert 'UI changes' in content
    assert 'business-domain mutation authority' in content
