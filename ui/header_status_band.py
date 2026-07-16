from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout

from app.engines.mission_control.header_status import (
    HeaderStatusViewModel,
    build_header_status_view_model,
)
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXStatusBadge,
    StatusTone,
)


HEADER_STATUS_STATE_LABELS = {
    'ready': ('Ready', StatusTone.POSITIVE),
    'unavailable': ('Unavailable', StatusTone.WARNING),
    'partial': ('Partial', StatusTone.WARNING),
    'error': ('Error-safe', StatusTone.NEGATIVE),
}


class HeaderStatusBand(MarketDEXDashboardPanel):
    """Compact read-only North Star-inspired Mission Control status band."""

    def __init__(
        self,
        view_model: HeaderStatusViewModel | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            'Command Status',
            'Read-only North Star header readiness',
            parent,
            tone=NorthStarPanelTone.COMMAND,
        )
        self.view_model = view_model or build_header_status_view_model()
        state_label, state_tone = HEADER_STATUS_STATE_LABELS[self.view_model.state]
        self.state_badge = MarketDEXStatusBadge(
            state_label,
            state_tone,
            self.content_widget,
        )
        self.headline_label = QLabel(self.view_model.headline, self.content_widget)
        self.headline_label.setObjectName('headerStatusHeadline')
        self.headline_label.setWordWrap(True)
        self.error_label = QLabel(self.view_model.error_text or '', self.content_widget)
        self.error_label.setObjectName('headerStatusErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')

        self.slot_row = QWidget(self.content_widget)
        self.slot_layout = QHBoxLayout(self.slot_row)
        self.slot_layout.setContentsMargins(0, 0, 0, 0)
        self.slot_layout.setSpacing(8)
        self.slot_labels: list[QLabel] = []
        self.slot_state_badges: list[MarketDEXStatusBadge] = []
        for slot in self.view_model.slots:
            slot_widget = QWidget(self.slot_row)
            slot_layout = QVBoxLayout(slot_widget)
            slot_layout.setContentsMargins(0, 0, 0, 0)
            slot_layout.setSpacing(2)
            slot_state_label, slot_state_tone = HEADER_STATUS_STATE_LABELS[slot.state]
            slot_state_badge = MarketDEXStatusBadge(
                slot_state_label,
                slot_state_tone,
                slot_widget,
            )
            label = QLabel(slot.label, slot_widget)
            label.setObjectName('headerStatusSlotLabel')
            detail = QLabel(slot.detail, slot_widget)
            detail.setObjectName('headerStatusSlotDetail')
            detail.setWordWrap(True)
            slot_layout.addWidget(slot_state_badge)
            slot_layout.addWidget(label)
            slot_layout.addWidget(detail)
            self.slot_state_badges.append(slot_state_badge)
            self.slot_labels.append(label)
            self.slot_labels.append(detail)
            self.slot_layout.addWidget(slot_widget)

        self.add_content_widget(self.state_badge)
        self.add_content_widget(self.headline_label)
        self.add_content_widget(self.error_label)
        self.add_content_widget(self.slot_row)
        slot_summary = '. '.join(
            f'{slot.label}: {slot.state}. {slot.detail}'
            for slot in self.view_model.slots
        )
        self.setAccessibleName(
            f'Command Status. {self.view_model.headline}. {slot_summary}'
        )
