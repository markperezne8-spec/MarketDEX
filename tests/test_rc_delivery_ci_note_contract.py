from pathlib import Path


def test_rc_delivery_ci_note_keeps_package_publication_manual():
    note = Path('docs/RC_DELIVERY_CI_NOTE.md').read_text(encoding='utf-8')

    assert 'intentionally manual (`workflow_dispatch`)' in note
    assert 'Pull-request CI protects its delivery contract' in note
    assert 'invoked after merge when an operator package is required' in note
    assert 'prevents every pull request from publishing a new operator package' in note
