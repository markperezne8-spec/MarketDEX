from pathlib import Path


def test_listing_workspace_test_matrix_is_complete():
    text = Path('docs/listing_workspace_test_matrix.md').read_text(encoding='utf-8')
    assert text.count('covered.') == 6
