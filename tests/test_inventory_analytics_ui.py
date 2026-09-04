import os
from datetime import datetime, timezone

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ui.inventory_analytics_feature import InventoryAnalyticsPanel

APP = QApplication.instance() or QApplication([])


def test_inventory_analytics_panel_renders_summary_and_chart_data():
    panel = InventoryAnalyticsPanel()
    panel.update_rows(
        [{
            "asset_name": "Pikachu",
            "asset_type": "SINGLE",
            "quantity": 2,
            "total_cost_minor": 1000,
            "online_market_price_minor": 2500,
            "online_market_price_status": "UPDATED",
            "online_market_updated_at": "2026-09-05T12:00:00+00:00",
            "listing_status": "Ready to List",
        }],
        now=datetime(2026, 9, 5, 12, tzinfo=timezone.utc),
    )
    assert panel.summary_values["total_units"].text() == "2"
    assert panel.summary_values["total_cost_minor"].text() == "$10.00"
    assert panel.summary_values["market_value_minor"].text() == "$50.00"
    assert panel.summary_values["estimated_profit_minor"].text() == "$40.00"
    assert panel.market_state.text().startswith("Market data: Updated")
    assert panel.category_chart.points[0]["label"] == "SINGLE"
    assert panel.status_chart.points[0]["label"] == "Ready to List"
    panel.close()
    panel.deleteLater()
    APP.processEvents()


def test_inventory_analytics_panel_shows_stale_price_state():
    panel = InventoryAnalyticsPanel()
    panel.update_rows(
        [{
            "asset_name": "Stale Card",
            "asset_type": "SINGLE",
            "quantity": 1,
            "total_cost_minor": 1000,
            "online_market_price_minor": 2500,
            "online_market_price_status": "UPDATED",
            "online_market_updated_at": "2026-09-03T10:00:00+00:00",
            "listing_status": "Not Listed",
        }],
        now=datetime(2026, 9, 5, 12, tzinfo=timezone.utc),
    )
    assert panel.summary_values["market_value_minor"].text() == "Price data stale"
    assert "Price data stale" in panel.market_state.text()
    assert panel.category_chart.points == []
    panel.close()
    panel.deleteLater()
    APP.processEvents()


def test_inventory_analytics_panel_empty_state():
    panel = InventoryAnalyticsPanel()
    panel.update_rows([], now=datetime(2026, 9, 5, 12, tzinfo=timezone.utc))
    assert panel.snapshot["market_value_state"] == "No data"
    assert panel.category_chart.empty_message.startswith("Price unavailable")
    assert panel.low_stock_chart.empty_message.startswith("No items")
    panel.close()
    panel.deleteLater()
    APP.processEvents()
