from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout

from app.engines.mission_control.todays_top3 import (
    TodaysTop3ViewModel,
    build_todays_top3_view_model,
)
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXStatusBadge,
    StatusTone,
)


TODAYS_TOP3_STATE_LABELS = {
    'ready': ('Ready', StatusTone.POSITIVE),
    'unavailable': ('Unavailable', StatusTone.WARNING),
    'partial': ('Partial', StatusTone.WARNING),
    'error': ('Error-safe', StatusTone.NEGATIVE),
}


class TodaysTop3Panel(MarketDEXDashboardPanel):
    """Compact read-only Mission Control attention-priority surface."""

    def __init__(
        self,
        view_model: TodaysTop3ViewModel | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            "Today's Top 3",
            'Read-only attention priorities',
            parent,
            tone=NorthStarPanelTone.COMMAND,
        )
        self.view_model = view_model or build_todays_top3_view_model()
        self.setProperty('dashboardRole', 'todays-top3-shell')
        self.setProperty('visualContract', 'm1.15c-todays-top3-display-states')
        self.setProperty('attentionState', self.view_model.state)
        state_label, state_tone = TODAYS_TOP3_STATE_LABELS[self.view_model.state]
        self.state_badge = MarketDEXStatusBadge(
            state_label,
            state_tone,
            self.content_widget,
        )
        self.headline_label = QLabel(self.view_model.headline, self.content_widget)
        self.headline_label.setObjectName('todaysTop3Headline')
        self.headline_label.setWordWrap(True)
        self.error_label = QLabel(self.view_model.error_text or '', self.content_widget)
        self.error_label.setObjectName('todaysTop3ErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')

        self.item_row = QWidget(self.content_widget)
        self.item_layout = QHBoxLayout(self.item_row)
        self.item_layout.setContentsMargins(0, 0, 0, 0)
        self.item_layout.setSpacing(8)
        self.item_labels: list[QLabel] = []
        self.item_state_badges: list[MarketDEXStatusBadge] = []
        for item in self.view_model.items:
            item_widget = MarketDEXDashboardPanel(
                f'#{item.rank} {item.title}',
                item.affected_area,
                self.item_row,
                tone=NorthStarPanelTone.SCOREBOARD,
            )
            item_widget.setProperty('dashboardRole', 'todays-top3-priority-card')
            item_widget.setProperty('priorityRank', item.rank)
            item_widget.setProperty('attentionState', item.state)
            item_widget.setProperty(
                'visualContract',
                'm1.15c-todays-top3-priority-card-state',
            )
            item_state_label, item_state_tone = TODAYS_TOP3_STATE_LABELS[item.state]
            item_state_badge = MarketDEXStatusBadge(
                item_state_label,
                item_state_tone,
                item_widget,
            )
            reason = QLabel(item.reason, item_widget)
            reason.setObjectName('todaysTop3Reason')
            reason.setWordWrap(True)
            evidence = QLabel(item.evidence_summary, item_widget)
            evidence.setObjectName('todaysTop3Evidence')
            evidence.setWordWrap(True)
            preparation = QLabel(item.next_safe_preparation, item_widget)
            preparation.setObjectName('todaysTop3Preparation')
            preparation.setWordWrap(True)
            item_widget.add_header_action(item_state_badge)
            item_widget.add_content_widget(reason)
            item_widget.add_content_widget(evidence)
            item_widget.add_content_widget(preparation)
            item_widget.setAccessibleName(
                f"Today's Top 3 rank {item.rank}. {item.title}. "
                f'{item.state}. {item.reason}. {item.evidence_summary}. '
                f'{item.next_safe_preparation}'
            )
            self.item_state_badges.append(item_state_badge)
            self.item_labels.extend(
                [
                    item_widget.title_label,
                    item_widget.description_label,
                    reason,
                    evidence,
                    preparation,
                ]
            )
            self.item_layout.addWidget(item_widget)

        self.add_content_widget(self.state_badge)
        self.add_content_widget(self.headline_label)
        self.add_content_widget(self.error_label)
        self.add_content_widget(self.item_row)
        item_summary = '. '.join(
            f'Rank {item.rank}: {item.title}: {item.state}. {item.reason}'
            for item in self.view_model.items
        )
        self.setAccessibleName(
            f"Today's Top 3. {self.view_model.headline}. {item_summary}"
        )
