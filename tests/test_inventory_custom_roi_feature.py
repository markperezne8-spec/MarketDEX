from ui.inventory_price_guidance_feature import price_guidance


def test_custom_roi_recalculates_recommended_price():
    twenty = price_guidance(5000, 12.75, 500, 100, 20.0)
    forty = price_guidance(5000, 12.75, 500, 100, 40.0)
    assert twenty['recommended_minor'] == 7565
    assert forty['recommended_minor'] == 8711
    assert forty['recommended_minor'] > twenty['recommended_minor']


def test_zero_roi_recommendation_covers_loaded_costs():
    result = price_guidance(5000, 13.25, 600, 100, 0.0)
    assert result['recommended_minor'] == result['break_even_minor']
