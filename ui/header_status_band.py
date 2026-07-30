from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QGridLayout, QVBoxLayout, QSizePolicy

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
    """Compact visual overview of Mission Control readiness."""

    def __init__(
        self,
        view_model: HeaderStatusViewModel | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            'Command Overview',
            'Live readiness across core MarketDEX systems',
            parent,
            tone=NorthStarPanelTone.COMMAND,
        )
        self.view_model = view_model or build_header_status_view_model()
        state_label, state_tone = HEADER_STATUS_STATE_LABELS[self.view_model.state]
        self.state_badge = MarketDEXStatusBadge(
            state_label,
            state_tone,
            self,
        )
        self.add_header_action(self.state_badge)

        self.headline_label = QLabel(self.view_model.headline, self.content_widget)
        self.headline_label.setObjectName('headerStatusHeadline')
        self.headline_label.setWordWrap(True)

        self.error_label = QLabel(self.view_model.error_text or '', self.content_widget)
        self.error_label.setObjectName('headerStatusErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')

        self.slot_row = QWidget(self.content_widget)
        self.slot_layout = QGridLayout(self.slot_row)
        self.slot_layout.setContentsMargins(0, 0, 0, 0)
        self.slot_layout.setHorizontalSpacing(10)
        self.slot_layout.setVerticalSpacing(8)
        self.slot_labels: list[QLabel] = []
        self.slot_state_badges: list[MarketDEXStatusBadge] = []

        for index, slot in enumerate(self.view_model.slots):
            slot_widget = QWidget(self.slot_row)
            slot_widget.setObjectName('headerStatusSlotCard')
            slot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            slot_layout = QVBoxLayout(slot_widget)
            slot_layout.setContentsMargins(12, 10, 12, 10)
            slot_layout.setSpacing(3)

            label = QLabel(slot.label, slot_widget)
            label.setObjectName('headerStatusSlotLabel')
            detail = QLabel(slot.detail, slot_widget)
            detail.setObjectName('headerStatusSlotDetail')
            detail.setWordWrap(True)
            slot_state_label, slot_state_tone = HEADER_STATUS_STATE_LABELS[slot.state]
            slot_state_badge = MarketDEXStatusBadge(
                slot_state_label,
                slot_state_tone,
                slot_widget,
            )

            slot_layout.addWidget(label)
            slot_layout.addWidget(detail)
            slot_layout.addWidget(slot_state_badge)
            slot_layout.addStretch(1)
            self.slot_state_badges.append(slot_state_badge)
            self.slot_labels.extend((label, detail))
            self.slot_layout.addWidget(slot_widget, index // 3, index % 3)

        self.add_content_widget(self.headline_label)
        self.add_content_widget(self.error_label)
        self.add_content_widget(self.slot_row)

        slot_summary = '. '.join(
            f'{slot.label}: {slot.state}. {slot.detail}'
            for slot in self.view_model.slots
        )
        self.setAccessibleName(
            f'Command Overview. {self.view_model.headline}. {slot_summary}'
        )
