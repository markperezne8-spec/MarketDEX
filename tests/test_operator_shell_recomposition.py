from pathlib import Path


def test_operator_shell_separates_mission_control_from_workspaces():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert "tabs.addTab(mission_page, 'Mission Control')" in source
    assert "tabs.addTab(inventory_page, 'Inventory & Pricing')" in source
    assert "tabs.addTab(listing_page, 'Listing Workflow')" in source
    assert 'MISSION CONTROL — YOUR BUSINESS AT A GLANCE' in source
    assert "box.hide()" in source
    assert "_refresh_mission_control(window)" in source
    assert "tabs.setCurrentIndex(1)" in source
    assert "tabs.setCurrentIndex(2)" in source
