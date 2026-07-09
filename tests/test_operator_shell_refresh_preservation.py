from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_shell_keeps_existing_refresh_button_and_does_not_add_refresh_logic():
    assert "refresh_button = getattr(window, 'refresh_button', None)" in SOURCE
    assert 'def refresh(' not in SOURCE
    assert '.snapshot()' not in SOURCE
