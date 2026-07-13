from pathlib import Path


def test_build700o_review_note_is_prebuild_only():
    document = Path('docs/Architecture/BUILD_700O_REVIEW_NOTE.md').read_text(encoding='utf-8')

    assert 'saved research query result preview boundary' in document
    assert 'no implementation yet' in document
    assert 'no visual verification' in document
