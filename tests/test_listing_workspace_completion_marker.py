from pathlib import Path


def test_completion_marker_is_ready_for_ci():
    text = Path('docs/listing_workspace_completion_marker.md').read_text(encoding='utf-8')
    assert 'ready for pull request review and CI' in text
