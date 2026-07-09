from pathlib import Path


def test_pricing_and_listing_tabs_are_not_selection_locked():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert 'tabs.setTabEnabled(1, selected)' not in source
    assert 'tabs.setTabEnabled(2, selected)' not in source
    assert "if not selected and tabs.currentIndex() != 0:" not in source
    assert "tabs.addTab(pricing_page, 'Pricing')" in source
    assert "tabs.addTab(listing_page, 'Listing Workflow')" in source
