from pathlib import Path


SOURCE = Path('ui/viewport_fit_feature.py').read_text(encoding='utf-8')


def test_operator_workspaces_follow_business_flow():
    mission = SOURCE.index("tabs.addTab(mission_page, 'Mission Control')")
    inventory = SOURCE.index("tabs.addTab(inventory_page, 'Inventory & Pricing')")
    listings = SOURCE.index("tabs.addTab(listing_page, 'Listings')")
    assert mission < inventory < listings
