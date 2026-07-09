from pathlib import Path


def test_operator_shell_pr_summary_describes_first_slice():
    summary = Path('docs/operator_shell_pr_summary.md').read_text(encoding='utf-8')

    assert 'Mission Control becomes the default first tab' in summary
    assert 'same eight values from the existing business snapshot service' in summary
    assert 'hidden rather than deleted' in summary
    assert 'sale completion behavior are preserved' in summary
