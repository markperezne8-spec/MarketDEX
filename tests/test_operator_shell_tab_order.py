from pathlib import Path


def test_operator_shell_tab_order_matches_handoff_indices():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    mission = source.index("tabs.addTab(mission_page, 'Mission Control')")
    inventory = source.index("tabs.addTab(inventory_page, 'Inventory & Pricing')")
    listing = source.index("tabs.addTab(listing_page, 'Listing Workflow')")
    assert mission < inventory < listing
    assert "inventory_button.clicked.connect(lambda: tabs.setCurrentIndex(1))" in source
    assert "continue_button.clicked.connect(lambda: tabs.setCurrentIndex(2))" in source
