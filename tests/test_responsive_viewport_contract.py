from pathlib import Path


def test_mission_control_has_no_fixed_820px_workspace_cap():
    source = Path('ui/main_window.py').read_text(encoding='utf-8')
    assert 'setMaximumWidth(820)' not in source
    assert 'QSizePolicy.Expanding' in source


def test_launcher_preserves_normal_window_resize_behavior():
    source = Path('launcher.py').read_text(encoding='utf-8')
    assert 'showMaximized()' not in source
    assert 'availableGeometry()' in source
    assert 'window.show()' in source
