from pathlib import Path


def test_pricing_workspace_is_a_dedicated_operator_destination():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert 'def _pricing_workspace(window, tabs):' in source
    assert "tabs.addTab(pricing_page, 'Pricing')" in source
    assert 'PRICE WITH COST, FEES, SHIPPING, PACKAGING, AND TARGET ROI IN VIEW' in source
    assert "continue_button.clicked.connect(lambda: tabs.setCurrentIndex(2))" in source
    assert "listings_button.clicked.connect(lambda: tabs.setCurrentIndex(3))" in source


def test_pricing_shell_does_not_import_business_authority():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    assert 'repositories.' not in source
    assert 'sqlite3' not in source
    assert 'services.' not in source
