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
