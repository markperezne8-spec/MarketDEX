from pathlib import Path


def test_operator_shell_document_preserves_authority_and_names_workspaces():
    text = Path('docs/operator-shell-recomposition.md').read_text(encoding='utf-8')
    assert 'SQLite authority' in text
    assert '**Mission Control**' in text
    assert '**Inventory & Pricing**' in text
    assert '**Listings**' in text
    assert 'does not create a second data path' in text
