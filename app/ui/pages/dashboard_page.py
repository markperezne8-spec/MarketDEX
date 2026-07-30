from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("missionControlPage")

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 32)
        root.setSpacing(24)

        title = QLabel("Mission Control")
        title.setObjectName("pageTitle")
        subtitle = QLabel("A focused view of your collection, inventory, and next business priorities.")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        root.addWidget(title)
        root.addWidget(subtitle)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(16)
        metrics.setVerticalSpacing(16)

        inventory_card, self.count = self._metric_card(
            "Inventory",
            "0",
            "Items currently tracked",
            "inventoryMetric",
        )
        portfolio_card, self.portfolio_value = self._metric_card(
            "Portfolio value",
            "$0.00",
            "Current recorded value",
            "portfolioMetric",
        )
        attention_card, self.attention_count = self._metric_card(
            "Needs attention",
            "0",
            "Records requiring review",
            "attentionMetric",
        )

        metrics.addWidget(inventory_card, 0, 0)
        metrics.addWidget(portfolio_card, 0, 1)
        metrics.addWidget(attention_card, 0, 2)
        metrics.setColumnStretch(0, 1)
        metrics.setColumnStretch(1, 1)
        metrics.setColumnStretch(2, 1)
        root.addLayout(metrics)

        status_panel = QFrame()
        status_panel.setObjectName("statusPanel")
        status_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        status_layout = QVBoxLayout(status_panel)
        status_layout.setContentsMargins(24, 22, 24, 22)
        status_layout.setSpacing(14)

        status_header = QHBoxLayout()
        status_title = QLabel("Operational status")
        status_title.setObjectName("sectionTitle")
        status_badge = QLabel("READY")
        status_badge.setObjectName("statusBadge")
        status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_header.addWidget(status_title)
        status_header.addStretch()
        status_header.addWidget(status_badge)

        status_copy = QLabel(
            "MarketDEX is ready for inventory work. Add or review assets to populate your business overview."
        )
        status_copy.setObjectName("statusCopy")
        status_copy.setWordWrap(True)

        next_step = QLabel("Next priority  •  Keep inventory records accurate and review items needing attention.")
        next_step.setObjectName("nextPriority")
        next_step.setWordWrap(True)

        status_layout.addLayout(status_header)
        status_layout.addWidget(status_copy)
        status_layout.addStretch()
        status_layout.addWidget(next_step)
        root.addWidget(status_panel, 1)

        self.setStyleSheet(
            """
            QWidget#missionControlPage {
                background: #0f172a;
                color: #f8fafc;
            }
            QLabel#pageTitle {
                color: #f8fafc;
                font-size: 30px;
                font-weight: 700;
            }
            QLabel#pageSubtitle {
                color: #94a3b8;
                font-size: 15px;
            }
            QFrame.metricCard, QFrame#statusPanel {
                background: #172033;
                border: 1px solid #29354d;
                border-radius: 14px;
            }
            QLabel.metricLabel {
                color: #94a3b8;
                font-size: 13px;
                font-weight: 600;
            }
            QLabel.metricValue {
                color: #f8fafc;
                font-size: 28px;
                font-weight: 700;
            }
            QLabel.metricDetail, QLabel#statusCopy {
                color: #a8b3c7;
                font-size: 13px;
            }
            QLabel#sectionTitle {
                color: #f8fafc;
                font-size: 18px;
                font-weight: 700;
            }
            QLabel#statusBadge {
                background: #183b35;
                color: #6ee7b7;
                border: 1px solid #285e52;
                border-radius: 10px;
                padding: 5px 10px;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#nextPriority {
                background: #101a2d;
                color: #dbeafe;
                border-left: 3px solid #3b82f6;
                border-radius: 6px;
                padding: 12px 14px;
                font-size: 13px;
            }
            """
        )

    @staticmethod
    def _metric_card(
        label_text: str,
        value_text: str,
        detail_text: str,
        value_object_name: str,
    ) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setProperty("class", "metricCard")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(138)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        label = QLabel(label_text)
        label.setProperty("class", "metricLabel")
        value = QLabel(value_text)
        value.setObjectName(value_object_name)
        value.setProperty("class", "metricValue")
        detail = QLabel(detail_text)
        detail.setProperty("class", "metricDetail")
        detail.setWordWrap(True)

        layout.addWidget(label)
        layout.addWidget(value)
        layout.addStretch()
        layout.addWidget(detail)
        return card, value
