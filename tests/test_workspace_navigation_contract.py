from pathlib import Path


def test_top_level_workspace_tabs_are_not_selection_locked():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')
    assert 'tabs.setTabEnabled(1, selected)' not in source
    assert 'tabs.setTabEnabled(2, selected)' not in source
    assert 'if not selected and tabs.currentIndex() != 0:' not in source


def test_top_level_workspaces_are_registered_through_the_canonical_registry():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert "('inventory', 'Inventory', 10)" in source
    assert "('pricing', 'Pricing', 20)" in source
    assert "('listing-workflow', 'Listing Workflow', 30)" in source
    assert 'for workspace in workspace_registry.all():' in source
    assert 'workspace_indexes[workspace.workspace_id] = tabs.addTab(page, workspace.title)' in source
    assert "tabs.addTab(inventory_page, 'Inventory')" not in source
    assert "tabs.addTab(pricing_page, 'Pricing')" not in source
    assert "tabs.addTab(listing_page, 'Listing Workflow')" not in source


def test_workspace_handoffs_navigate_by_stable_workspace_identity():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert "_activate_workspace(window, 'pricing')" in source
    assert "_activate_workspace(window, 'listing-workflow')" in source
    assert 'tabs.setCurrentIndex(1)' not in source
    assert 'tabs.setCurrentIndex(2)' not in source
