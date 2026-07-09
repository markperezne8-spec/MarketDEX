from pathlib import Path


def test_workspace_recomposition_documents_current_and_next_boundaries():
    text = Path('docs/operator_workspace_recomposition.md').read_text(encoding='utf-8')
    assert 'Sales — marketplace listing outcomes and confirmed sale completion.' in text
    assert 'Separate Inventory and Pricing into focused workspaces' in text
