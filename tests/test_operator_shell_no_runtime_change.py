from pathlib import Path


def test_operator_shell_contract_documents_presentation_only_boundary():
    text = Path('docs/operator-shell-recomposition.md').read_text(encoding='utf-8')
    assert 'presentation-boundary recomposition' in text
    assert 'does not create a second data path' in text
