from pathlib import Path


def test_inventory_workspace_exposes_explicit_listing_workflow_handoff():
    feature = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert "QGroupBox('🚀 NEXT: LISTING WORKFLOW')" in feature
    assert "QPushButton('Continue to Listing Workflow →')" in feature
    assert "tabs.setCurrentIndex(1)" in feature
    assert "panel_layout.insertWidget(panel_layout.indexOf(window.refresh_button), handoff)" in feature


def test_handoff_is_installed_after_listing_tab_exists():
    feature = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    listing_tab = "tabs.addTab(listing_page, 'Listing Workflow')"
    handoff_install = '_install_listing_workflow_handoff(window, tabs)'
    assert feature.index(listing_tab) < feature.rindex(handoff_install)
