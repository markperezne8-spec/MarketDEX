from pathlib import Path


def test_listing_workspace_scope_excludes_publishing():
    text = Path('docs/listing_workspace_scope.md').read_text(encoding='utf-8')
    assert 'Not included' in text
    assert 'marketplace publishing' in text
