import pytest

from ui.inventory_profit_feature import profit_decision
from ui.inventory_price_guidance_feature import price_guidance


SCENARIOS = [
    ("Charizard ex single", 2200, 3999, 13.25, 500, 100, 669),
    ("Pikachu low-value single", 125, 249, 12.75, 73, 15, 4),
    ("Elite Trainer Box", 5200, 7999, 13.25, 900, 150, 689),
    ("Booster pack", 425, 600, 12.75, 73, 15, 11),
    ("Overpaid chase card", 8000, 6999, 13.25, 500, 100, -2528),
    ("Bulk energy lot", 300, 1200, 12.75, 500, 100, 147),
    ("Free promotional card", 0, 499, 12.75, 73, 15, 347),
    ("High-fee marketplace item", 4500, 7000, 18.0, 600, 100, 540),
]


@pytest.mark.parametrize("name,cost,sale,fee,shipping,packaging,expected_profit", SCENARIOS)
def test_realistic_inventory_profit_scenarios(name, cost, sale, fee, shipping, packaging, expected_profit):
    result = profit_decision(cost, sale, fee, shipping, packaging)
    assert result["net_profit_minor"] == expected_profit, name
    assert result["fees_minor"] == round(sale * fee / 100), name


def test_zero_cost_inventory_has_defined_roi_behavior():
    result = profit_decision(0, 499, 12.75, 73, 15)
    assert result["net_profit_minor"] == 347
    assert result["roi_percent"] == 0.0


def test_price_guidance_round_trips_to_target_roi_or_better():
    for name, cost, _sale, fee, shipping, packaging, _expected_profit in SCENARIOS:
        guidance = price_guidance(cost, fee, shipping, packaging, 20.0)
        result = profit_decision(cost, guidance["recommended_minor"], fee, shipping, packaging)
        if cost > 0:
            assert result["roi_percent"] >= 20.0, name
        assert guidance["minimum_profit_minor"] > guidance["break_even_minor"], name
        assert guidance["recommended_minor"] >= guidance["minimum_profit_minor"], name


def test_quantity_rollup_uses_per_unit_profit_consistently():
    quantity = 24
    per_unit = profit_decision(425, 600, 12.75, 73, 15)
    assert per_unit["net_profit_minor"] == 11
    assert per_unit["net_profit_minor"] * quantity == 264


def test_zero_quantity_inventory_does_not_create_unit_cost_division():
    quantity = 0
    total_cost_minor = 3000
    unit_cost_minor = 0 if quantity <= 0 else round(total_cost_minor / quantity)
    assert unit_cost_minor == 0
    result = price_guidance(unit_cost_minor, 13.25, 500, 100)
    assert result["break_even_minor"] == 692
