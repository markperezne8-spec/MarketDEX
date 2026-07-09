from pathlib import Path


def test_windows_rc_delivery_is_manual_and_operator_facing():
    workflow = Path('.github/workflows/windows-rc-delivery.yml').read_text(encoding='utf-8')

    assert 'workflow_dispatch:' in workflow
    assert 'runs-on: windows-latest' in workflow
    assert "dist/MarketDEX.exe" in workflow
    assert 'Stage operator delivery package' in workflow
    assert 'README.txt' in workflow
    assert 'outside the MarketDEX source repository' in workflow
    assert 'MarketDEX-Windows-RC-Operator-Package' in workflow
    assert 'if-no-files-found: error' in workflow


def test_windows_rc_delivery_document_preserves_source_authority():
    document = Path('docs/WINDOWS_RC_OPERATOR_DELIVERY.md').read_text(encoding='utf-8')

    assert 'Git repository remains source authority' in document
    assert '`MarketDEX.exe` remains a generated build product' in document
    assert 'operator extracts and runs the package outside the source repository' in document
    assert 'source-controlled binaries' in document
