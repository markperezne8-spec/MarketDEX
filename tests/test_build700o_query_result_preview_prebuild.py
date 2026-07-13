from pathlib import Path


def test_build700o_query_result_preview_prebuild_contract():
    document = Path(
        'docs/Architecture/BUILD_700O_QUERY_RESULT_PREVIEW_PREBUILD.md'
    ).read_text(encoding='utf-8')

    required_phrases = (
        'source saved query definitions only from the composition-owned `ResearchQueryCatalog`',
        'source evidence only from approved offline fixture observations',
        'in-memory and non-persistent',
        'execute live marketplace queries',
        'persist saved query definitions or preview results',
        'add editing, import, delete, run, refresh, or automation controls',
        'one saved query definition can display matching offline fixture evidence',
        'Not required for Build 700O because this build is documentation-only',
    )

    for phrase in required_phrases:
        assert phrase in document
