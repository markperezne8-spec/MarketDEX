from ui.inventory_listing_workspace_feature import listing_workspace_summary
from ui.inventory_price_guidance_feature import price_guidance


def test_summary_marks_exact_recommendation():
    recommended = price_guidance(1000, 20.0, 500, 100, 20.0)['recommended_minor']
    text = listing_workspace_summary('Asset', 'CUSTOM', recommended, recommended, 1000, 20.0, 'SALE READY')
    assert 'ON RECOMMENDATION' in text
