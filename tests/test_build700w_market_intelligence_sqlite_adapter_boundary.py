from pathlib import Path


def test_build700w_market_intelligence_sqlite_adapter_boundary_contract():
    document = Path(
        'docs/Architecture/BUILD_700W_MARKET_INTELLIGENCE_SQLITE_ADAPTER_BOUNDARY.md'
    ).read_text(encoding='utf-8')

    required_phrases = (
        'without implementing SQLite connections, SQL, schema, migrations, adapters, repositories, or database writes',
        'explicit transaction boundaries for write operations',
        'deterministic conversion between SQLite rows and immutable warehouse domain models',
        'preserve append-only observation and snapshot history',
        'use idempotency keys or stable identifiers',
        'roll back the complete transaction when any required write fails',
        'preserve exact source attribution and provenance links',
        'Build 700W does not authorize any schema or migration implementation',
        'must not silently drop records, partially commit related writes',
        'Not required because Build 700W is documentation/test-only',
    )

    for phrase in required_phrases:
        assert phrase in document
