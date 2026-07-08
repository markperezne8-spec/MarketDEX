from pathlib import Path


def test_next_boundary_is_saved_listing_plans():
    text = Path('docs/listing_workspace_next_boundary.md').read_text(encoding='utf-8')
    assert 'save listing plans' in text
    assert 'sale completion separate' in text
