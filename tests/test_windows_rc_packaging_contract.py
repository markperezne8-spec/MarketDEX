from pathlib import Path


def test_windows_rc_packaging_contract_is_present():
    spec = Path('MarketDEX.spec').read_text(encoding='utf-8')
    build_requirements = Path('requirements-build.txt').read_text(encoding='utf-8')
    workflow = Path('.github/workflows/ci.yml').read_text(encoding='utf-8')

    assert "['launcher.py']" in spec
    assert "name='MarketDEX'" in spec
    assert 'console=False' in spec
    assert '-r requirements.txt' in build_requirements
    assert 'pyinstaller==' in build_requirements
    assert 'runs-on: windows-latest' in workflow
    assert 'dist/MarketDEX.exe' in workflow
