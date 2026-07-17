from pathlib import Path


def test_launcher_opens_main_window_maximized_after_screen_bounded_size_seed():
    launcher = (Path(__file__).parents[1] / 'launcher.py').read_text(encoding='utf-8')

    assert 'availableGeometry()' in launcher
    assert 'window.resize(' in launcher
    assert 'min(1280, available_geometry.width())' in launcher
    assert 'min(800, available_geometry.height())' in launcher
    assert 'window.showMaximized()' in launcher
    assert 'window.show()' not in launcher
