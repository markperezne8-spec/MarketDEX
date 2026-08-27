from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy

from app.engines.mission_control.operational_status import (
    OperationalStatusViewModel,
    build_operational_status_view_model,
)
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXStatusBadge,
    StatusTone,
)

OPERATIONAL_STATUS_STATE_LABELS = {
    'available': ('Ready', StatusTone.POSITIVE),
    'unavailable': ('Unavailable', StatusTone.WARNING),
    'partial': ('Partial', StatusTone.WARNING),
    'error': ('Error-safe', StatusTone.NEGATIVE),
}

OPERATIONAL_STATUS_GROUP_STATE_LABELS = {
    'available': ('Available', StatusTone.POSITIVE),
    'unavailable': ('Unavailable', StatusTone.WARNING),
    'partial': ('Partial', StatusTone.WARNING),
    'error': ('Error-safe', StatusTone.NEGATIVE),
}


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
        state_label, state_tone = OPERATIONAL_STATUS_STATE_LABELS[
            self.view_model.state
        ]
        self.state_badge = MarketDEXStatusBadge(state_label, state_tone, self)
        self.add_header_action(self.state_badge)

        self.headline_label = QLabel(self.view_model.headline, self.content_widget)
        self.headline_label.setObjectName('operationalStatusHeadline')
        self.headline_label.setWordWrap(True)
        self.error_label = QLabel(self.view_model.error_text or '', self.content_widget)
        self.error_label.setObjectName('operationalStatusErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')

        self.group_row = QWidget(self.content_widget)
        self.group_layout = QGridLayout(self.group_row)
        self.group_layout.setContentsMargins(0, 0, 0, 0)
        self.group_layout.setHorizontalSpacing(8)
        self.group_layout.setVerticalSpacing(8)
        self.group_layout.setColumnStretch(0, 1)
        self.group_layout.setColumnStretch(1, 1)
        self.group_labels: list[QLabel] = []
        self.group_state_badges: list[MarketDEXStatusBadge] = []
        for index, group in enumerate(self.view_model.groups):
            group_widget = QFrame(self.group_row)
            group_widget.setObjectName('marketdexKpiCard')
            group_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            group_layout = QVBoxLayout(group_widget)
            group_layout.setContentsMargins(12, 10, 12, 10)
            group_layout.setSpacing(3)

            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(6)
            label = QLabel(group.label, group_widget)
            label.setObjectName('operationalStatusGroupLabel')
            group_state_label, group_state_tone = OPERATIONAL_STATUS_GROUP_STATE_LABELS[
                group.state
            ]
            group_state_badge = MarketDEXStatusBadge(
                group_state_label,
                group_state_tone,
                group_widget,
            )
            header.addWidget(label, 1)
            header.addWidget(group_state_badge)

            detail = QLabel(group.detail, group_widget)
            detail.setObjectName('operationalStatusGroupDetail')
            detail.setWordWrap(True)
            group_layout.addLayout(header)
            group_layout.addWidget(detail)
            group_layout.addStretch(1)

            self.group_state_badges.append(group_state_badge)
            self.group_labels.extend((label, detail))
            self.group_layout.addWidget(group_widget, index // 2, index % 2)

        self.add_content_widget(self.headline_label)
        self.add_content_widget(self.error_label)
        self.add_content_widget(self.group_row)
        group_summary = '. '.join(
            f'{group.label}: {group.state}. {group.detail}'
            for group in self.view_model.groups
        )
        self.setAccessibleName(
            f'Operational Status. {self.view_model.headline}. {group_summary}'
        )
