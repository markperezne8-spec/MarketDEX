from pathlib import Path


def test_build700o_merge_note_requires_green_ci_only():
    document = Path('docs/Architecture/BUILD_700O_MERGE_NOTE.md').read_text(encoding='utf-8')

    assert 'Merge only after CI is green' in document
    assert 'documentation-only' in document
    assert 'requires no visual verification' in document
