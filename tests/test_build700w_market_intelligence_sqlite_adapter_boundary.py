from pathlib import Path


def test_build700w_market_intelligence_sqlite_adapter_boundary_contract():
    document = Path(
        'docs/Architecture/BUILD_700W_MARKET_INTELLIGENCE_SQLITE_ADAPTER_BOUNDARY.md'
    ).read_text(encoding='utf-8')

    required_phrases = (
        'without implementing SQLite connections, SQL, schema, migrations, repository adapters, or database writes',
        'SQLite connection acquisition for the Market Intelligence warehouse only',
        'explicit transaction scopes for future write operations',
        'schema-version compatibility checks before reads or writes',
        'deterministic row-to-domain mapping for warehouse models',
        'commit atomically or roll back completely',
        'be idempotent for repeated ingestion attempts',
        'reject conflicting duplicate identifiers instead of rewriting history in place',
        'return immutable warehouse domain models instead of raw rows',
        'support repository interface filters without leaking SQL details to callers',
        'schema version is unknown or unsupported',
        'Application services must remain the entry point for repository use',
        'Build 700W must not',
        'Not required for Build 700W because this build is documentation/test-only',
    )

    for phrase in required_phrases:
        assert phrase in document
