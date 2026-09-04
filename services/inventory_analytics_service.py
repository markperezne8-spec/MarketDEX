"""Derived analytics for the filtered Inventory projection.

Only stored online prices with status UPDATED and an observation no older than
24 hours are used for market value. Missing and stale prices remain unavailable.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping

PRICE_STALE_AFTER = timedelta(hours=24)
LOW_STOCK_THRESHOLD = 2


def _int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_timestamp(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _online_price_state(row: Mapping[str, Any], now: datetime) -> tuple[int | None, str]:
    status = str(row.get("online_market_price_status", "") or "").strip().upper()
    updated_at = _parse_timestamp(row.get("online_market_updated_at"))
    if status in {"PRICE_STALE", "STALE"}:
        return None, "stale"
    if status != "UPDATED" or row.get("online_market_price_minor") is None:
        return None, "unavailable"
    if updated_at is None or now - updated_at > PRICE_STALE_AFTER:
        return None, "stale"
    price = _int_value(row.get("online_market_price_minor"), -1)
    if price < 0:
        return None, "unavailable"
    return price, "available"


def _point(label: str, value_minor: int | None, state: str = "") -> dict[str, Any]:
    return {"label": label, "value_minor": value_minor, "state": state}


def calculate_inventory_analytics(
    rows: Iterable[Mapping[str, Any]],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build deterministic chart data from the already-filtered inventory rows."""
    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    materialized = [dict(row) for row in rows]
    total_units = sum(_int_value(row.get("quantity")) for row in materialized)
    total_cost_minor = sum(_int_value(row.get("total_cost_minor")) for row in materialized)

    available_rows: list[tuple[dict[str, Any], int]] = []
    unavailable_count = 0
    stale_count = 0
    for row in materialized:
        price, price_state = _online_price_state(row, current_time)
        if price_state == "available":
            available_rows.append((row, price or 0))
        elif price_state == "stale":
            stale_count += 1
        else:
            unavailable_count += 1

    available_market_value = sum(
        price * _int_value(row.get("quantity")) for row, price in available_rows
    )
    has_market_value = bool(available_rows)
    market_value_minor = available_market_value if has_market_value else None
    if not materialized:
        market_value_state = "No data"
    elif unavailable_count == 0 and stale_count == 0:
        market_value_state = "Updated"
    elif not has_market_value and stale_count:
        market_value_state = "Price data stale"
    elif not has_market_value:
        market_value_state = "Price unavailable"
    else:
        market_value_state = f"Partial • {unavailable_count} unavailable • {stale_count} stale"

    estimated_profit_minor = (
        available_market_value - total_cost_minor
        if materialized and unavailable_count == 0 and stale_count == 0
        else None
    )

    category_values: dict[str, int] = {}
    for row, price in available_rows:
        category = str(
            row.get("asset_type") or row.get("category") or "Uncategorized"
        ).strip() or "Uncategorized"
        category_values[category] = category_values.get(category, 0) + (
            price * _int_value(row.get("quantity"))
        )
    category_points = [
        _point(label, value)
        for label, value in sorted(
            category_values.items(), key=lambda item: (-item[1], item[0].casefold())
        )
    ]

    status_counts: dict[str, int] = {}
    for row in materialized:
        status = str(row.get("listing_status") or "Not Listed").strip() or "Not Listed"
        status_counts[status] = status_counts.get(status, 0) + _int_value(row.get("quantity"))
    status_points = [
        _point(label, value)
        for label, value in sorted(
            status_counts.items(), key=lambda item: item[0].casefold()
        )
    ]

    profit_points = [
        _point(
            str(row.get("asset_name") or "Unnamed item"),
            price * _int_value(row.get("quantity"))
            - _int_value(row.get("total_cost_minor")),
        )
        for row, price in available_rows
    ]
    profit_points.sort(
        key=lambda item: (-_int_value(item["value_minor"]), item["label"].casefold())
    )

    low_stock_points = [
        _point(str(row.get("asset_name") or "Unnamed item"), _int_value(row.get("quantity")))
        for row in materialized
        if _int_value(row.get("quantity")) <= LOW_STOCK_THRESHOLD
    ]
    low_stock_points.sort(
        key=lambda item: (_int_value(item["value_minor"]), item["label"].casefold())
    )

    market_empty_message = (
        "Price data stale — no current market values in this filtered view."
        if stale_count and not has_market_value
        else "Price unavailable — no current market values in this filtered view."
    )
    return {
        "asset_count": len(materialized),
        "total_units": total_units,
        "total_cost_minor": total_cost_minor,
        "market_value_minor": market_value_minor,
        "estimated_profit_minor": estimated_profit_minor,
        "market_value_state": market_value_state,
        "price_unavailable_count": unavailable_count,
        "price_stale_count": stale_count,
        "cost_vs_market": [
            _point("Total Cost", total_cost_minor),
            _point("Market Value", market_value_minor, "" if market_value_minor is not None else market_value_state),
        ],
        "category_market_value": category_points,
        "quantity_by_listing_status": status_points,
        "top_estimated_profit": profit_points[:10],
        "low_stock": low_stock_points,
        "market_empty_message": market_empty_message,
    }
