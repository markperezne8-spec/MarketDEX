from pathlib import Path


def test_build700o_refresh_conflict_note_remains_non_runtime():
    document = Path('docs/Architecture/BUILD_700O_REFRESH_CONFLICT_NOTE.md').read_text(encoding='utf-8')

    assert 'original draft branch predated the Build 700N merge' in document
    assert 'documentation boundary only' in document
    assert 'no Market Intelligence UI edits' in document
    assert 'no catalog fixture edits' in document
    assert 'no persistence or execution authority' in document
