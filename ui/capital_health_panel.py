from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout

from app.engines.mission_control.capital_health import (
    CapitalHealthViewModel,
    build_capital_health_view_model,
)
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXStatusBadge,
    StatusTone,
)


CAPITAL_HEALTH_STATE_LABELS = {
    'ready': ('Ready', StatusTone.POSITIVE),
    'unavailable': ('Unavailable', StatusTone.WARNING),
    'partial': ('Partial', StatusTone.WARNING),
    'error': ('Error-safe', StatusTone.NEGATIVE),
}


class CapitalHealthPanel(MarketDEXDashboardPanel):
    """Compact read-only Mission Control capital condition surface."""

    def __init__(
        self,
        view_model: CapitalHealthViewModel | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            'Capital Health',
            'Read-only capital condition',
            parent,
            tone=NorthStarPanelTone.SCOREBOARD,
        )
        self.view_model = view_model or build_capital_health_view_model()
        self.setProperty('dashboardRole', 'capital-health-shell')
        self.setProperty('visualContract', 'm1.16b-capital-health-shell')
        self.setProperty('capitalHealthState', self.view_model.state)
        state_label, state_tone = CAPITAL_HEALTH_STATE_LABELS[self.view_model.state]
        self.state_badge = MarketDEXStatusBadge(
            state_label,
            state_tone,
            self.content_widget,
        )
        self.headline_label = QLabel(self.view_model.headline, self.content_widget)
        self.headline_label.setObjectName('capitalHealthHeadline')
        self.headline_label.setWordWrap(True)
        self.error_label = QLabel(self.view_model.error_text or '', self.content_widget)
        self.error_label.setObjectName('capitalHealthErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')

        self.group_row = QWidget(self.content_widget)
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
            group_widget.setProperty('dashboardRole', 'capital-health-group-card')
            group_widget.setProperty('capitalHealthGroup', group.group)
            group_widget.setProperty('capitalHealthState', group.state)
            group_widget.setProperty(
                'visualContract',
                'm1.16b-capital-health-group-card',
            )
            group_state_label, group_state_tone = CAPITAL_HEALTH_STATE_LABELS[
                group.state
            ]
            group_state_badge = MarketDEXStatusBadge(
                group_state_label,
                group_state_tone,
                group_widget,
            )
            evidence = QLabel(group.evidence_summary, group_widget)
            evidence.setObjectName('capitalHealthEvidence')
            evidence.setWordWrap(True)
            source = QLabel(group.source_authority, group_widget)
            source.setObjectName('capitalHealthSourceAuthority')
            source.setWordWrap(True)
            explanation = QLabel(group.explanation, group_widget)
            explanation.setObjectName('capitalHealthExplanation')
            explanation.setWordWrap(True)
            metrics = QWidget(group_widget)
            metric_layout = QVBoxLayout(metrics)
            metric_layout.setContentsMargins(0, 0, 0, 0)
            metric_layout.setSpacing(4)
            for metric in group.metrics:
                metric_label = QLabel(
                    f'{metric.label}: {metric.value_label} — {metric.evidence_summary}',
                    metrics,
                )
                metric_label.setObjectName('capitalHealthMetric')
                metric_label.setWordWrap(True)
                metric_label.setProperty('capitalHealthState', metric.state)
                metric_layout.addWidget(metric_label)
                self.metric_labels.append(metric_label)

            group_widget.add_header_action(group_state_badge)
            group_widget.add_content_widget(evidence)
            group_widget.add_content_widget(source)
            group_widget.add_content_widget(explanation)
            group_widget.add_content_widget(metrics)
            group_widget.setAccessibleName(
                f'Capital Health {group.title}. {group.state}. '
                f'{group.evidence_summary}. {group.source_authority}. '
                f'{group.explanation}'
            )
            self.group_state_badges.append(group_state_badge)
            self.group_labels.extend(
                [
                    group_widget.title_label,
                    group_widget.description_label,
                    evidence,
                    source,
                    explanation,
                ]
            )
            self.group_layout.addWidget(group_widget)

        self.add_content_widget(self.state_badge)
        self.add_content_widget(self.headline_label)
        self.add_content_widget(self.error_label)
        self.add_content_widget(self.group_row)
        group_summary = '. '.join(
            f'{group.title}: {group.state}. {group.evidence_summary}'
            for group in self.view_model.groups
        )
        self.setAccessibleName(
            f'Capital Health. {self.view_model.headline}. {group_summary}'
        )
