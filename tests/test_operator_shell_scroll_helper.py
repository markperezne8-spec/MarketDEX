from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_workspace_pages_share_one_scroll_construction_path():
    assert 'def _scroll_page(widget, parent):' in SOURCE
    assert SOURCE.count('_scroll_page(') == 4
    assert 'scroll.setWidgetResizable(True)' in SOURCE
