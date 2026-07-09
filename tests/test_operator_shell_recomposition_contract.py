from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_operator_shell_exposes_business_workspaces():
    assert "tabs.addTab(mission_page, 'Mission Control')" in SOURCE
    assert "tabs.addTab(inventory_page, 'Inventory & Pricing')" in SOURCE
    assert "tabs.addTab(listing_page, 'Listings')" in SOURCE


def test_mission_control_is_extracted_from_inventory_workspace():
    assert 'mission_control = _extract_mission_control(window)' in SOURCE
    assert 'panel_layout.takeAt(0)' in SOURCE
    assert 'dashboard_layout.addLayout(cards_item.layout())' in SOURCE


def test_inventory_handoff_targets_listing_workspace_by_index():
    assert 'listing_index = tabs.addTab' in SOURCE
    assert '_install_listing_workflow_handoff(window, tabs, listing_index)' in SOURCE
    assert 'tabs.setCurrentIndex(listing_index)' in SOURCE
