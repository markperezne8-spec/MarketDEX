from pathlib import Path


def test_launcher_opens_main_window_with_screen_bounded_rc_geometry():
    launcher = (Path(__file__).parents[1] / 'launcher.py').read_text(encoding='utf-8')

    assert 'availableGeometry()' in launcher
    assert 'window.resize(' in launcher
    assert 'min(1280, available_geometry.width())' in launcher
    assert 'min(800, available_geometry.height())' in launcher
    assert 'window.show()' in launcher
    assert 'window.showMaximized()' not in launcher
