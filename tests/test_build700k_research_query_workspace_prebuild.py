from pathlib import Path


def test_build700k_research_query_workspace_prebuild_contract():
    document = Path(
        'docs/Architecture/BUILD_700K_RESEARCH_QUERY_WORKSPACE_PREBUILD.md'
    ).read_text(encoding='utf-8')

    required_phrases = (
        'read-only presentation of saved research query definitions',
        'Product Registry remains the authority for canonical `product_id` identity',
        'must not\n\n- create, edit, delete, import, or persist definitions',
        'no database file, migration, provider call, timer, or mutation is introduced',
        'Build 700L implementation gate',
        'Not required for Build 700K because this build is documentation-only',
    )

    for phrase in required_phrases:
        assert phrase in document
