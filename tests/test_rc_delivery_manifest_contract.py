from pathlib import Path


def test_rc_delivery_manifest_matches_operator_package():
    manifest = Path('docs/RC_DELIVERY_MANIFEST.md').read_text(encoding='utf-8')

    assert '`MarketDEX-Windows-RC-Operator-Package`' in manifest
    assert '`MarketDEX.exe`' in manifest
    assert '`README.txt`' in manifest
    assert 'does not contain source code' in manifest
    assert 'or an installer' in manifest
