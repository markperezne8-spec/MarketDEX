from pathlib import Path


def test_rc_operator_note_keeps_pull_and_binary_actions_unambiguous():
    note = Path('docs/WINDOWS_RC_DELIVERY_OPERATOR_NOTE.md').read_text(encoding='utf-8')

    assert '🟢 PULL NOW' in note
    assert 'extract it outside the repository' in note
    assert 'Never merge `MarketDEX.exe` into the Git repository' in note
