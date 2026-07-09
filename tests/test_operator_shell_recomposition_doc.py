from pathlib import Path


def test_operator_shell_recomposition_documents_preserved_authority():
    document = Path('docs/operator_shell_recomposition.md').read_text(encoding='utf-8')

    assert 'business-at-a-glance entry point' in document
    assert 'without duplicating business logic or persistence authority' in document
    assert 'services, repositories, SQLite authority' in document
    assert 'sale completion boundaries are unchanged' in document
