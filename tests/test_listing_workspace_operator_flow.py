from pathlib import Path


def test_operator_flow_ends_with_consolidated_summary():
    text = Path('docs/listing_workspace_operator_flow.md').read_text(encoding='utf-8')
    assert text.strip().endswith('summary.')
