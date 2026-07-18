from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout

from app.engines.mission_control.business_scoreboard import (
    BUSINESS_SCOREBOARD_GROUP_ORDER,
    BusinessScoreboardState,
    BusinessScoreboardViewModel,
    build_business_scoreboard_view_model,
)
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXStatusBadge,
    StatusTone,
)


BUSINESS_SCOREBOARD_VISUAL_CONTRACT = 'm1.18b-business-scoreboard-shell'
BUSINESS_SCOREBOARD_GROUP_VISUAL_CONTRACT = 'm1.18b-business-scoreboard-group-shell'
BUSINESS_SCOREBOARD_METRIC_VISUAL_CONTRACT = 'm1.18b-business-scoreboard-metric-shell'

BUSINESS_SCOREBOARD_STATE_LABELS: dict[BusinessScoreboardState, tuple[str, StatusTone]] = {
    'ready': ('Ready', StatusTone.POSITIVE),
    'unavailable': ('Unavailable', StatusTone.WARNING),
    'partial': ('Partial', StatusTone.WARNING),
    'not_applicable': ('Not applicable', StatusTone.INFORMATION),
    'error': ('Error-safe', StatusTone.NEGATIVE),
}


def business_scoreboard_state_badge_contract(
    state: BusinessScoreboardState,
) -> tuple[str, StatusTone]:
    try:
        return BUSINESS_SCOREBOARD_STATE_LABELS[state]
    except KeyError as exc:
        raise ValueError('unsupported Business Scoreboard display state') from exc


class BusinessScoreboardPanel(MarketDEXDashboardPanel):
    """Compact read-only Mission Control period performance surface."""

    def __init__(
        self,
        view_model: BusinessScoreboardViewModel | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            'Business Scoreboard',
            'Read-only period performance',
            parent,
            tone=NorthStarPanelTone.SCOREBOARD,
        )
        self.view_model = view_model or build_business_scoreboard_view_model()
        self.setProperty('dashboardRole', 'business-scoreboard-shell')
        self.setProperty('visualContract', BUSINESS_SCOREBOARD_VISUAL_CONTRACT)
        self.setProperty('businessScoreboardState', self.view_model.state)
        self.setProperty(
            'businessScoreboardGroupOrder',
            ','.join(BUSINESS_SCOREBOARD_GROUP_ORDER),
        )
        state_label, state_tone = business_scoreboard_state_badge_contract(
            self.view_model.state
        )
        self.state_badge = MarketDEXStatusBadge(
            state_label,
            state_tone,
            self.content_widget,
        )
        self.state_badge.setProperty('businessScoreboardState', self.view_model.state)
        self.state_badge.setProperty('businessScoreboardDisplayLabel', state_label)
        self.period_label = QLabel(
            f'Selected period: {self.view_model.selected_period_label}',
            self.content_widget,
        )
        self.period_label.setObjectName('businessScoreboardPeriod')
        self.period_label.setWordWrap(True)
        self.headline_label = QLabel(self.view_model.headline, self.content_widget)
        self.headline_label.setObjectName('businessScoreboardHeadline')
        self.headline_label.setWordWrap(True)
        self.error_label = QLabel(self.view_model.error_text or '', self.content_widget)
        self.error_label.setObjectName('businessScoreboardErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')

        self.group_row = QWidget(self.content_widget)
        self.group_row.setProperty(
            'businessScoreboardGroupOrder',
            ','.join(BUSINESS_SCOREBOARD_GROUP_ORDER),
        )
        self.group_layout = QHBoxLayout(self.group_row)
        self.group_layout.setContentsMargins(0, 0, 0, 0)
        self.group_layout.setSpacing(8)
        self.group_labels: list[QLabel] = []
        self.group_state_badges: list[MarketDEXStatusBadge] = []
        self.metric_labels: list[QLabel] = []

        for group in self.view_model.groups:
            group_widget = MarketDEXDashboardPanel(
                group.title,
                group.period_label,
                self.group_row,
                tone=NorthStarPanelTone.SCOREBOARD,
            )
            group_widget.setProperty('dashboardRole', 'business-scoreboard-group-card')
            group_widget.setProperty('businessScoreboardGroup', group.group)
            group_widget.setProperty('businessScoreboardState', group.state)
            group_widget.setProperty(
                'visualContract',
                BUSINESS_SCOREBOARD_GROUP_VISUAL_CONTRACT,
            )
            group_state_label, group_state_tone = business_scoreboard_state_badge_contract(
                group.state
            )
            group_state_badge = MarketDEXStatusBadge(
                group_state_label,
                group_state_tone,
                group_widget,
            )
            group_state_badge.setProperty('businessScoreboardState', group.state)
            group_state_badge.setProperty(
                'businessScoreboardDisplayLabel',
                group_state_label,
            )
            evidence = QLabel(group.evidence_summary, group_widget)
            evidence.setObjectName('businessScoreboardEvidence')
            evidence.setWordWrap(True)
            source = QLabel(group.source_authority, group_widget)
            source.setObjectName('businessScoreboardSourceAuthority')
            source.setWordWrap(True)
            metrics = QWidget(group_widget)
            metric_layout = QVBoxLayout(metrics)
            metric_layout.setContentsMargins(0, 0, 0, 0)
            metric_layout.setSpacing(4)

            for metric in group.metrics:
                metric_state_label, metric_state_tone = (
                    business_scoreboard_state_badge_contract(metric.state)
                )
                metric_label = QLabel(
                    (
                        f'{metric_state_label} - {metric.label}: {metric.value_label}. '
                        f'{metric.period_label}. Evidence: {metric.evidence_summary} '
                        f'Source: {metric.source_authority}. '
                        f'Calculation: {metric.calculation_authority}.'
                    ),
                    metrics,
                )
                metric_label.setObjectName('businessScoreboardMetric')
                metric_label.setWordWrap(True)
                metric_label.setProperty('businessScoreboardGroup', group.group)
                metric_label.setProperty('businessScoreboardState', metric.state)
                metric_label.setProperty(
                    'businessScoreboardDisplayLabel',
                    metric_state_label,
                )
                metric_label.setProperty(
                    'businessScoreboardStateTone',
                    metric_state_tone.value,
                )
                metric_label.setProperty(
                    'visualContract',
                    BUSINESS_SCOREBOARD_METRIC_VISUAL_CONTRACT,
                )
                metric_layout.addWidget(metric_label)
                self.metric_labels.append(metric_label)

            group_widget.add_header_action(group_state_badge)
            group_widget.add_content_widget(evidence)
            group_widget.add_content_widget(source)
            group_widget.add_content_widget(metrics)
            group_widget.setAccessibleName(
                f'Business Scoreboard {group.title}. {group.state}. '
                f'{group.period_label}. {group.evidence_summary}. '
                f'{group.source_authority}'
            )
            self.group_state_badges.append(group_state_badge)
            self.group_labels.extend(
                [
                    group_widget.title_label,
                    group_widget.description_label,
                    evidence,
                    source,
                ]
            )
            self.group_layout.addWidget(group_widget)

        self.add_content_widget(self.state_badge)
        self.add_content_widget(self.period_label)
        self.add_content_widget(self.headline_label)
        self.add_content_widget(self.error_label)
        self.add_content_widget(self.group_row)
        group_summary = '. '.join(
            f'{group.title}: {group.state}. {group.evidence_summary}'
            for group in self.view_model.groups
        )
        self.setAccessibleName(
            f'Business Scoreboard. {self.view_model.selected_period_label}. '
            f'{self.view_model.headline}. {group_summary}'
        )
