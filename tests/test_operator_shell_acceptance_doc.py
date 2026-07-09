from pathlib import Path


def test_operator_shell_visual_acceptance_is_explicit():
    document = Path('docs/operator_shell_acceptance.md').read_text(encoding='utf-8')

    assert 'dedicated Mission Control tab' in document
    assert 'eight authoritative business snapshot values' in document
    assert 'one explicit next-action button' in document
    assert 'SQLite authority behavior is changed by this slice' in document
