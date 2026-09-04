from datetime import datetime, timedelta, timezone

from services.inventory_analytics_service import LOW_STOCK_THRESHOLD, calculate_inventory_analytics

NOW = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)


def _row(name, *, asset_type="SINGLE", quantity=1, cost=1000, price=5000, updated_at=None, status="UPDATED", listing_status="Not Listed"):
    return {
        "asset_id": name.lower().replace(" ", "-"),
        "asset_name": name,
        "asset_type": asset_type,
        "quantity": quantity,
        "total_cost_minor": cost,
        "online_market_price_minor": price,
        "online_market_price_status": status,
        "online_market_updated_at": updated_at or NOW.isoformat(),
        "listing_status": listing_status,
    }


def test_inventory_analytics_calculates_totals_categories_statuses_profit_and_low_stock():
    rows = [
        _row("Charizard ex", quantity=1, cost=1000, price=5000, listing_status="Ready to List"),
        _row("Mega ETB", asset_type="SEALED", quantity=3, cost=6000, price=3000, listing_status="Listed"),
        _row("Pikachu slab", asset_type="SLAB", quantity=2, cost=7000, price=12000, listing_status="Hold"),
    ]
    snapshot = calculate_inventory_analytics(rows, now=NOW)
    assert snapshot["asset_count"] == 3
    assert snapshot["total_units"] == 6
    assert snapshot["total_cost_minor"] == 14000
    assert snapshot["market_value_minor"] == 38000
    assert snapshot["estimated_profit_minor"] == 24000
    assert snapshot["market_value_state"] == "Updated"
    assert [(p["label"], p["value_minor"]) for p in snapshot["category_market_value"]] == [
        ("SLAB", 24000), ("SEALED", 9000), ("SINGLE", 5000)
    ]
    assert [(p["label"], p["value_minor"]) for p in snapshot["quantity_by_listing_status"]] == [
        ("Hold", 2), ("Listed", 3), ("Ready to List", 1)
    ]
    assert snapshot["top_estimated_profit"][0] == {"label": "Pikachu slab", "value_minor": 17000, "state": ""}
    assert [p["label"] for p in snapshot["low_stock"]] == ["Charizard ex", "Pikachu slab"]
    assert LOW_STOCK_THRESHOLD == 2


def test_inventory_analytics_marks_missing_and_stale_prices_without_fallbacks():
    rows = [
        _row("Current", cost=500, price=1500),
        _row("Stale", cost=600, price=9000, updated_at=(NOW - timedelta(hours=25)).isoformat()),
        _row("Unavailable", cost=700, price=None, status="CREDENTIALS_MISSING", updated_at=""),
    ]
    snapshot = calculate_inventory_analytics(rows, now=NOW)
    assert snapshot["market_value_minor"] == 1500
    assert snapshot["estimated_profit_minor"] is None
    assert snapshot["price_stale_count"] == 1
    assert snapshot["price_unavailable_count"] == 1
    assert snapshot["market_value_state"] == "Partial • 1 unavailable • 1 stale"
    assert snapshot["category_market_value"] == [{"label": "SINGLE", "value_minor": 1500, "state": ""}]
    assert snapshot["top_estimated_profit"][0]["label"] == "Current"


def test_inventory_analytics_follows_the_existing_filtered_projection():
    rows = [
        _row("Sealed ETB", asset_type="SEALED", quantity=2, cost=4000, price=7000),
        _row("Single Card", asset_type="SINGLE", quantity=1, cost=500, price=3000),
    ]
    filtered_rows = [row for row in rows if row["asset_type"] == "SEALED" and "etb" in row["asset_name"].casefold()]
    snapshot = calculate_inventory_analytics(filtered_rows, now=NOW)
    assert snapshot["asset_count"] == 1
    assert snapshot["total_units"] == 2
    assert snapshot["market_value_minor"] == 14000
    assert snapshot["low_stock"][0]["label"] == "Sealed ETB"


def test_inventory_analytics_empty_data_has_explicit_chart_empty_states():
    snapshot = calculate_inventory_analytics([], now=NOW)
    assert snapshot["asset_count"] == 0
    assert snapshot["total_units"] == 0
    assert snapshot["total_cost_minor"] == 0
    assert snapshot["market_value_minor"] is None
    assert snapshot["estimated_profit_minor"] is None
    assert snapshot["market_value_state"] == "No data"
    assert snapshot["category_market_value"] == []
    assert snapshot["quantity_by_listing_status"] == []
    assert snapshot["top_estimated_profit"] == []
    assert snapshot["low_stock"] == []
