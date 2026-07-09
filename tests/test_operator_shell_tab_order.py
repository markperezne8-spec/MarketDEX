from pathlib import Path


def test_operator_shell_tab_order_matches_handoff_indices():
    source = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')

    mission = source.index("tabs.addTab(mission_page, 'Mission Control')")
    inventory = source.index("tabs.addTab(inventory_page, 'Inventory')")
    pricing = source.index("tabs.addTab(pricing_page, 'Pricing')")
    listings = source.index("tabs.addTab(listing_page, 'Listings')")
    sales = source.index("tabs.addTab(sales_page, 'Sales')")
    assert mission < inventory < pricing < listings < sales
    assert "inventory_button.clicked.connect(lambda: tabs.setCurrentIndex(1))" in source
    assert "continue_button.clicked.connect(lambda: tabs.setCurrentIndex(2))" in source
    assert "listings_button.clicked.connect(lambda: tabs.setCurrentIndex(3))" in source
