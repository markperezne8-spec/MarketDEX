from pathlib import Path


def test_windows_rc_delivery_is_manual_prerelease_boundary():
    workflow = Path('.github/workflows/windows-rc-delivery.yml').read_text(encoding='utf-8')

    assert 'workflow_dispatch:' in workflow
    assert 'contents: write' in workflow
    assert 'python -m PyInstaller --clean --noconfirm MarketDEX.spec' in workflow
    assert 'Verify release candidate executable' in workflow
    assert 'gh release create' in workflow
    assert 'dist/MarketDEX.exe' in workflow
    assert '--prerelease' in workflow
    assert 'Download MarketDEX.exe and launch it directly.' in workflow
