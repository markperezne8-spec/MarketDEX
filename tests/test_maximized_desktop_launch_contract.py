from pathlib import Path


def test_launcher_opens_main_window_maximized():
    launcher = (Path(__file__).parents[1] / 'launcher.py').read_text(encoding='utf-8')

    assert 'window.showMaximized()' in launcher
    assert 'window.resize(' not in launcher
    assert 'window.show()' not in launcher
