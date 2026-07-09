from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_inventory_workspace_reuses_existing_central_content():
    assert 'content = window.takeCentralWidget()' in SOURCE
    assert '_scroll_page(content, tabs)' in SOURCE
    assert 'window.inventory_panel.layout()' in SOURCE
