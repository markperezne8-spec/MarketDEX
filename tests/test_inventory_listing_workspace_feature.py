from ui.inventory_listing_workspace_feature import listing_workspace_summary


def test_listing_workspace_consolidates_operator_decision():
    summary = listing_workspace_summary('Test ETB', 'EBAY', 8000, 7565, 1380, 27.6, 'SALE READY')
    assert 'Test ETB' in summary
    assert 'EBAY' in summary
    assert 'ABOVE RECOMMENDATION $4.35' in summary
    assert 'Net $13.80' in summary
    assert 'ROI 27.6%' in summary
    assert 'SALE READY' in summary


def test_listing_workspace_flags_below_recommendation():
    summary = listing_workspace_summary('Card', 'TCGPLAYER', 6000, 7000, -500, -10.0, 'LOSS')
    assert 'BELOW RECOMMENDATION $10.00' in summary
    assert 'LOSS' in summary
