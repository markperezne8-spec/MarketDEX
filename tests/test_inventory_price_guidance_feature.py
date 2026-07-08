from ui.inventory_price_guidance_feature import price_guidance


def test_price_guidance_is_fee_and_cost_aware():
    result = price_guidance(5000, 12.75, 500, 100)
    assert result['break_even_minor'] == 6419
    assert result['minimum_profit_minor'] == 6420
    assert result['recommended_minor'] == 7565


def test_price_guidance_rises_with_selling_costs():
    base = price_guidance(5000, 0, 0, 0)
    loaded = price_guidance(5000, 13.25, 600, 100)
    assert loaded['break_even_minor'] > base['break_even_minor']
    assert loaded['recommended_minor'] > base['recommended_minor']
