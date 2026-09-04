"""Inventory analytics view built from the existing filtered inventory projection."""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)
from services.inventory_analytics_service import LOW_STOCK_THRESHOLD, calculate_inventory_analytics


class InventoryAnalyticsChart(QWidget):
    """Small dependency-free horizontal bar chart for the dark desktop UI."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.chart_title = title
        self.points: list[dict[str, Any]] = []
        self.empty_message = "Not enough data to display this chart."
        self.setMinimumHeight(225)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAccessibleName(title)

    def set_points(self, points: list[dict[str, Any]], empty_message: str = "Not enough data to display this chart.") -> None:
        self.points = list(points)
        self.empty_message = empty_message
        self.update()

    @staticmethod
    def _money(value_minor: int) -> str:
        return "$" + "{:,.2f}".format(int(value_minor) / 100)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        frame = self.rect().adjusted(1, 1, -1, -1)
        painter.setPen(QPen(QColor("#1d8fe1"), 1))
        painter.setBrush(QColor("#0b1f36"))
        painter.drawRoundedRect(frame, 8, 8)
        painter.setPen(QColor("#e6f2ff"))
        painter.drawText(14, 25, self.chart_title)
        if not self.points:
            painter.setPen(QColor("#9bb0c8"))
            painter.drawText(
                self.rect().adjusted(16, 46, -16, -16),
                Qt.AlignCenter | Qt.TextWordWrap,
                self.empty_message,
            )
            painter.end()
            return
        bar_left = 148
        value_right = self.width() - 12
        bar_width = max(50, value_right - bar_left - 92)
        max_value = max(1, max(abs(int(point.get("value_minor") or 0)) for point in self.points))
        row_height = max(24, min(34, (self.height() - 58) // max(1, len(self.points))))
        for index, point in enumerate(self.points):
            y = 45 + index * row_height
            label = str(point.get("label") or "—")
            if len(label) > 20:
                label = label[:19] + "…"
            painter.setPen(QColor("#cfe1f5"))
            painter.drawText(12, y + 18, label)
            value = point.get("value_minor")
            state = str(point.get("state") or "")
            if value is None:
                painter.setPen(QColor("#f0b429"))
                painter.drawText(bar_left, y + 18, state or "Price unavailable")
                continue
            numeric_value = int(value)
            width = int(bar_width * abs(numeric_value) / max_value)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#f0b429" if numeric_value < 0 else "#21d4fd"))
            painter.drawRoundedRect(bar_left, y + 5, max(2, width), 18, 4, 4)
            painter.setPen(QColor("#e6f2ff"))
            painter.drawText(value_right - 82, y + 18, self._money(numeric_value))
        painter.end()


class InventoryAnalyticsPanel(QWidget):
    """Summary and chart panel synchronized with Inventory filters."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("inventoryAnalyticsPanel")
        self.setProperty("visualContract", "inventory-analytics-charts-826")
        self.setProperty("dashboardRole", "inventory-analytics")
        self.setAccessibleName("Inventory analytics and charts")
        self.snapshot: dict[str, Any] = {}
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 8, 0, 8)
        root.setSpacing(8)
        title = QLabel("INVENTORY ANALYTICS")
        title.setStyleSheet("font-size:18px;font-weight:700;color:#21d4fd;")
        root.addWidget(title)
        self.market_state = QLabel("Market data: No data")
        self.market_state.setWordWrap(True)
        root.addWidget(self.market_state)
        summary = QHBoxLayout()
        self.summary_values: dict[str, QLabel] = {}
        for label, key in (("Units", "total_units"), ("Total Cost", "total_cost_minor"), ("Market Value", "market_value_minor"), ("Est. Profit", "estimated_profit_minor")):
            card = QGroupBox(label)
            card.setObjectName("inventoryAnalyticsMetricCard")
            card_layout = QVBoxLayout(card)
            value = QLabel("—")
            value.setStyleSheet("font-size:17px;font-weight:700;")
            card_layout.addWidget(value)
            summary.addWidget(card)
            self.summary_values[key] = value
        root.addLayout(summary)
        charts = QGridLayout()
        charts.setHorizontalSpacing(8)
        charts.setVerticalSpacing(8)
        charts.setColumnStretch(0, 1)
        charts.setColumnStretch(1, 1)
        self.cost_chart = InventoryAnalyticsChart("Total Cost vs Market Value")
        self.category_chart = InventoryAnalyticsChart("Inventory Value by Category")
        self.status_chart = InventoryAnalyticsChart("Quantity by Listing Status")
        self.profit_chart = InventoryAnalyticsChart("Top 10 Items by Estimated Profit")
        self.low_stock_chart = InventoryAnalyticsChart("Low-Stock Items (≤{} units)".format(LOW_STOCK_THRESHOLD))
        charts.addWidget(self.cost_chart, 0, 0)
        charts.addWidget(self.category_chart, 0, 1)
        charts.addWidget(self.status_chart, 1, 0)
        charts.addWidget(self.profit_chart, 1, 1)
        charts.addWidget(self.low_stock_chart, 2, 0, 1, 2)
        root.addLayout(charts)

    @staticmethod
    def _money(value_minor: int) -> str:
        return "$" + "{:,.2f}".format(int(value_minor) / 100)

    def _summary_value(self, value: int | None, state: str) -> str:
        return state if value is None else self._money(value)

    def update_rows(self, rows: list[dict[str, Any]], *, now=None) -> None:
        self.snapshot = calculate_inventory_analytics(rows, now=now)
        snapshot = self.snapshot
        state = snapshot["market_value_state"]
        self.summary_values["total_units"].setText("{:,}".format(snapshot["total_units"]))
        self.summary_values["total_cost_minor"].setText(self._money(snapshot["total_cost_minor"]))
        self.summary_values["market_value_minor"].setText(self._summary_value(snapshot["market_value_minor"], state))
        self.summary_values["estimated_profit_minor"].setText(self._summary_value(snapshot["estimated_profit_minor"], state))
        if state == "Updated":
            status_text = "Market data: Updated — only stored prices from the last 24 hours are included."
        elif state == "Price data stale":
            status_text = "Market data: Price data stale — older observations are excluded."
        elif state == "Price unavailable":
            status_text = "Market data: Price unavailable — no stored current prices are available."
        elif state == "No data":
            status_text = "Market data: No filtered inventory items."
        else:
            status_text = "Market data: {} — incomplete prices are excluded from totals.".format(state)
        self.market_state.setText(status_text)
        self.cost_chart.set_points(snapshot["cost_vs_market"], snapshot["market_empty_message"])
        self.category_chart.set_points(snapshot["category_market_value"], snapshot["market_empty_message"])
        self.status_chart.set_points(snapshot["quantity_by_listing_status"], "No listing-status quantities in this filtered view.")
        self.profit_chart.set_points(snapshot["top_estimated_profit"], snapshot["market_empty_message"])
        self.low_stock_chart.set_points(snapshot["low_stock"], "No items at or below {} units.".format(LOW_STOCK_THRESHOLD))


def install_inventory_analytics_feature(window) -> None:
    if getattr(window, "inventory_analytics_installed", False):
        return
    window.inventory_analytics_installed = True
    panel = InventoryAnalyticsPanel(window.inventory_panel)
    window.inventory_analytics_panel = panel
    inventory_layout = window.inventory_panel.layout()
    inventory_layout.insertWidget(inventory_layout.indexOf(window.inventory_table), panel)
    panel.setVisible(False)
    toggle = QPushButton("Inventory Analytics")
    toggle.setCheckable(True)
    window.inventory_analytics_button = toggle

    def toggle_panel(checked: bool) -> None:
        panel.setVisible(checked)
        toggle.setText("Hide Analytics" if checked else "Inventory Analytics")

    toggle.clicked.connect(toggle_panel)
    action_layout = window.inventory_workspace_controls.action_layout
    action_layout.insertWidget(max(0, action_layout.count() - 1), toggle)

    def update_from_current_rows(*_args) -> None:
        panel.update_rows(window.inventory_rows)

    for signal in (
        window.inventory_search.textChanged,
        window.inventory_type_filter.currentTextChanged,
        window.inventory_condition_filter.currentTextChanged,
        window.inventory_sort.currentTextChanged,
        window.inventory_sort_order.currentTextChanged,
        window.inventory_listing_status_filter.currentTextChanged,
        window.inventory_listing_marketplace_filter.currentTextChanged,
        window.inventory_listing_draft_status_filter.currentTextChanged,
    ):
        signal.connect(update_from_current_rows)

    original_refresh_inventory = window.refresh_inventory

    def refresh_inventory_with_analytics(*args, **kwargs):
        result = original_refresh_inventory(*args, **kwargs)
        panel.update_rows(window.inventory_rows)
        return result

    window.refresh_inventory = refresh_inventory_with_analytics
    panel.update_rows(window.inventory_rows)
