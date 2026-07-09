from pathlib import Path


def test_operator_shell_change_is_confined_to_presentation_feature():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')
    assert 'def install_viewport_fit_feature(window):' in source
    assert 'window.setCentralWidget(tabs)' in source
