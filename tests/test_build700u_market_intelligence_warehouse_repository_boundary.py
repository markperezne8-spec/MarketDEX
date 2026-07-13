from pathlib import Path


def test_build700u_market_intelligence_warehouse_repository_boundary_contract():
    document = Path(
        'docs/Architecture/BUILD_700U_MARKET_INTELLIGENCE_WAREHOUSE_REPOSITORY_BOUNDARY.md'
    ).read_text(encoding='utf-8')

    required_phrases = (
        'without implementing repository interfaces, persistence, migrations, or database writes',
        'separate read responsibilities from write responsibilities',
        'append-only ingestion of normalized warehouse observations',
        'use explicit transaction boundaries',
        'be idempotent for repeated import or ingestion attempts',
        'reference canonical Product Registry product IDs without becoming product identity authority',
        'retrieving read-only saved-query preview history',
        'keep saved research query definitions separate from observation storage',
        'add repository protocols, interfaces, implementations, or adapters',
        'Not required for Build 700U because this build is documentation/test-only',
    )

    for phrase in required_phrases:
        assert phrase in document
