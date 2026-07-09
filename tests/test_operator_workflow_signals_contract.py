from pathlib import Path


def test_operator_workflow_signals_protect_pull_and_binary_boundaries():
    contract = Path('docs/OPERATOR_WORKFLOW_SIGNALS.md').read_text(encoding='utf-8')

    assert '🟢 PULL NOW' in contract
    assert '⬇️ NO PULL' in contract
    assert 'only after `main` has genuinely advanced' in contract
    assert 'Generated executables remain outside the source repository' in contract
