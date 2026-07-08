from pathlib import Path


def test_pr_summary_names_consolidated_decision_signals():
    text = Path('docs/listing_workspace_pr_summary.md').read_text(encoding='utf-8')
    for signal in ('marketplace', 'target price position', 'true net profit', 'ROI', 'sale readiness'):
        assert signal in text
