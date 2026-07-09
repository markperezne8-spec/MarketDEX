from pathlib import Path


def test_rc_delivery_scope_preserves_source_and_delivery_authority():
    scope = Path('docs/RC_DELIVERY_SCOPE.md').read_text(encoding='utf-8')

    assert 'IN SCOPE: manual Windows RC package generation' in scope
    assert 'OUT OF SCOPE: committing binaries' in scope
    assert 'installer engineering' in scope
    assert 'Git remains source authority' in scope
    assert 'Windows package is a delivery product' in scope
