from pathlib import Path


def test_build700o_clean_branch_note_is_documentation_only():
    document = Path('docs/Architecture/BUILD_700O_CLEAN_BRANCH_NOTE.md').read_text(encoding='utf-8')

    assert 'after Build 700N merged into `main`' in document
    assert 'only documentation and documentation tests' in document
