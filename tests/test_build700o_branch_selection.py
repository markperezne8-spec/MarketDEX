from pathlib import Path


def test_build700o_branch_selection_rejects_stale_draft_branch():
    document = Path('docs/Architecture/BUILD_700O_BRANCH_SELECTION.md').read_text(encoding='utf-8')

    assert 'Use the clean Build 700O branch' in document
    assert 'earlier stale draft branch must not be merged' in document
    assert 'before Build 700N landed on `main`' in document
