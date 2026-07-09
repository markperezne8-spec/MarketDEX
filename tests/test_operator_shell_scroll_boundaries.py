from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_each_operator_workspace_has_its_own_scroll_boundary():
    assert '_scroll_page(mission_control, tabs)' in SOURCE
    assert '_scroll_page(content, tabs)' in SOURCE
    assert '_scroll_page(listing_content, tabs)' in SOURCE
    assert 'marketdex_mission_control_scroll' in SOURCE
    assert 'marketdex_listing_workflow_scroll' in SOURCE
