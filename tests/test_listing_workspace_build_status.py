from pathlib import Path


def test_build_status_records_complete_feature_branch():
    text = Path('docs/listing_workspace_build_status.md').read_text(encoding='utf-8')
    assert 'Implementation complete' in text
    assert 'connected UI response' in text
