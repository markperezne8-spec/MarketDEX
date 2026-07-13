from pathlib import Path


def test_build700o_refresh_note_preserves_documentation_only_scope():
    document = Path('docs/Architecture/BUILD_700O_REFRESH_NOTE.md').read_text(encoding='utf-8')

    required_phrases = (
        'supersedes the stale Build 700O draft branch',
        'documentation-only',
        'no UI implementation',
        'no query execution',
        'no persistence',
        'no live provider access',
        'no automated actions',
    )

    for phrase in required_phrases:
        assert phrase in document
