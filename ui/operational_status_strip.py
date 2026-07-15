from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout

from app.engines.mission_control.operational_status import (
    OperationalStatusViewModel,
    build_operational_status_view_model,
)
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXStatusBadge,
    StatusTone,
)


class OperationalStatusStrip(MarketDEXDashboardPanel):
    """Compact read-only Mission Control operational readiness strip."""

    def __init__(
        self,
        view_model: OperationalStatusViewModel | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            'Operational Status',
            'Read-only local readiness snapshot',
            parent,
        )
        self.view_model = view_model or build_operational_status_view_model()
        state_labels = {
            'available': ('Ready', StatusTone.POSITIVE),
            'unavailable': ('Unavailable', StatusTone.WARNING),
            'partial': ('Partial', StatusTone.WARNING),
            'error': ('Error-safe', StatusTone.NEGATIVE),
        }
        state_label, state_tone = state_labels[self.view_model.state]
        self.state_badge = MarketDEXStatusBadge(
            state_label,
            state_tone,
            self.content_widget,
        )
        self.headline_label = QLabel(self.view_model.headline, self.content_widget)
        self.headline_label.setObjectName('operationalStatusHeadline')
        self.headline_label.setWordWrap(True)
        self.error_label = QLabel(self.view_model.error_text or '', self.content_widget)
        self.error_label.setObjectName('operationalStatusErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')

        self.group_row = QWidget(self.content_widget)
        self.group_layout = QHBoxLayout(self.group_row)
        self.group_layout.setContentsMargins(0, 0, 0, 0)
        self.group_layout.setSpacing(8)
        self.group_labels: list[QLabel] = []
        for group in self.view_model.groups:
            group_widget = QWidget(self.group_row)
            group_layout = QVBoxLayout(group_widget)
            group_layout.setContentsMargins(0, 0, 0, 0)
            group_layout.setSpacing(2)
            label = QLabel(group.label, group_widget)
            label.setObjectName('operationalStatusGroupLabel')
            detail = QLabel(group.detail, group_widget)
            detail.setObjectName('operationalStatusGroupDetail')
            detail.setWordWrap(True)
            group_layout.addWidget(label)
            group_layout.addWidget(detail)
            self.group_labels.append(label)
            self.group_labels.append(detail)
            self.group_layout.addWidget(group_widget)

        self.add_content_widget(self.state_badge)
        self.add_content_widget(self.headline_label)
        self.add_content_widget(self.error_label)
        self.add_content_widget(self.group_row)
        group_summary = '. '.join(
            f'{group.label}: {group.detail}' for group in self.view_model.groups
        )
        self.setAccessibleName(
            f'Operational Status. {self.view_model.headline}. {group_summary}'
        )
