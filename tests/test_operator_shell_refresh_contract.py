from pathlib import Path


def test_mission_control_refresh_wraps_existing_refresh_authority():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert 'original_refresh = window.refresh' in source
    assert 'original_refresh()' in source
    assert 'snapshot = window.service.snapshot()' in source
    assert 'window.refresh = refresh' in source
