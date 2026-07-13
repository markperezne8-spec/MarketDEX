from pathlib import Path


DOC_PATH = Path('docs/market_intelligence_sqlite_migration_plan.md')


def test_market_intelligence_sqlite_migration_plan_defines_boundaries() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    required_phrases = [
        'planning-only',
        'does not create executable migrations',
        'Schema-version checks must happen before repository writes',
        'sources, because provenance depends on source identity',
        'provenance, because observations depend on capture/source attribution',
        'observations, because snapshots and preview history depend on immutable evidence rows',
        'saved-query preview history',
        'Future migrations must be atomic per migration step',
        'Product Registry authority',
        'repository interface boundaries',
        'no live providers, credentials, scraping, alerts, schedulers, or cloud sync',
    ]

    for phrase in required_phrases:
        assert phrase in content


def test_market_intelligence_sqlite_migration_plan_blocks_implementation_scope() -> None:
    content = DOC_PATH.read_text(encoding='utf-8')

    non_goals = [
        'no SQL files',
        'no SQLite connections',
        'no executable migrations',
        'no repository adapters',
        'no repository implementations',
        'no seed data',
        'no imports or writes',
        'no UI changes',
    ]

    for phrase in non_goals:
        assert phrase in content
