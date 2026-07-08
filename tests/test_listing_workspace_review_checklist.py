from pathlib import Path


def test_review_checklist_covers_five_workspace_controls():
    text = Path('docs/listing_workspace_review_checklist.md').read_text(encoding='utf-8')
    assert text.count('- ') == 5
