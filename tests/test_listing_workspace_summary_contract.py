from ui.inventory_listing_workspace_feature import listing_workspace_summary


def test_summary_marks_exact_recommendation():
    text = listing_workspace_summary('Asset', 'CUSTOM', 7000, 7000, 1000, 20.0, 'SALE READY')
    assert 'ON RECOMMENDATION' in text
