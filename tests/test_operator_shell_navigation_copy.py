from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_shell_uses_operator_facing_navigation_language():
    assert "'Mission Control'" in SOURCE
    assert "'Inventory & Pricing'" in SOURCE
    assert "'Listings'" in SOURCE
    assert 'Continue to Listings →' in SOURCE
    assert 'protected SQLite authority' not in SOURCE
    assert 'authoritative SOLD boundary' not in SOURCE
