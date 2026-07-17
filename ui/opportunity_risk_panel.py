from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout

from app.engines.mission_control.opportunity_risk import (
    OPPORTUNITY_RISK_KIND_ORDER,
    OpportunityRiskState,
    OpportunityRiskViewModel,
    build_opportunity_risk_view_model,
)
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXStatusBadge,
    StatusTone,
)


OPPORTUNITY_RISK_VISUAL_CONTRACT = 'm1.17b-opportunity-risk-shell'
OPPORTUNITY_RISK_GROUP_VISUAL_CONTRACT = 'm1.17b-opportunity-risk-group-shell'
OPPORTUNITY_RISK_ITEM_VISUAL_CONTRACT = 'm1.17b-opportunity-risk-item-shell'

OPPORTUNITY_RISK_STATE_LABELS: dict[OpportunityRiskState, tuple[str, StatusTone]] = {
    'ready': ('Ready', StatusTone.POSITIVE),
    'unavailable': ('Unavailable', StatusTone.WARNING),
    'partial': ('Partial', StatusTone.WARNING),
    'error': ('Error-safe', StatusTone.NEGATIVE),
}


def opportunity_risk_state_badge_contract(
    state: OpportunityRiskState,
) -> tuple[str, StatusTone]:
    try:
        return OPPORTUNITY_RISK_STATE_LABELS[state]
    except KeyError as exc:
        raise ValueError('unsupported Opportunity + Risk display state') from exc


class OpportunityRiskPanel(MarketDEXDashboardPanel):
    """Compact read-only Mission Control Opportunity + Risk surface."""

    def __init__(
        self,
        view_model: OpportunityRiskViewModel | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            'Opportunity + Risk',
            'Read-only situational awareness',
            parent,
            tone=NorthStarPanelTone.SCOREBOARD,
        )
        self.view_model = view_model or build_opportunity_risk_view_model()
        self.setProperty('dashboardRole', 'opportunity-risk-shell')
        self.setProperty('visualContract', OPPORTUNITY_RISK_VISUAL_CONTRACT)
        self.setProperty('opportunityRiskState', self.view_model.state)
        self.setProperty(
            'opportunityRiskGroupOrder',
            ','.join(OPPORTUNITY_RISK_KIND_ORDER),
        )
        state_label, state_tone = opportunity_risk_state_badge_contract(
            self.view_model.state
        )
        self.state_badge = MarketDEXStatusBadge(
            state_label,
            state_tone,
            self.content_widget,
        )
        self.state_badge.setProperty('opportunityRiskState', self.view_model.state)
        self.state_badge.setProperty('opportunityRiskDisplayLabel', state_label)
        self.headline_label = QLabel(self.view_model.headline, self.content_widget)
        self.headline_label.setObjectName('opportunityRiskHeadline')
        self.headline_label.setWordWrap(True)
        self.error_label = QLabel(self.view_model.error_text or '', self.content_widget)
        self.error_label.setObjectName('opportunityRiskErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')

        self.group_row = QWidget(self.content_widget)
        self.group_row.setProperty(
            'opportunityRiskGroupOrder',
            ','.join(OPPORTUNITY_RISK_KIND_ORDER),
        )
        self.group_layout = QHBoxLayout(self.group_row)
        self.group_layout.setContentsMargins(0, 0, 0, 0)
        self.group_layout.setSpacing(8)
        self.group_labels: list[QLabel] = []
        self.group_state_badges: list[MarketDEXStatusBadge] = []
        self.item_labels: list[QLabel] = []

        for group in self.view_model.groups:
            group_widget = MarketDEXDashboardPanel(
                group.title,
                group.freshness_label,
                self.group_row,
                tone=NorthStarPanelTone.SCOREBOARD,
            )
            group_widget.setProperty('dashboardRole', 'opportunity-risk-group-card')
            group_widget.setProperty('opportunityRiskKind', group.kind)
            group_widget.setProperty('opportunityRiskState', group.state)
            group_widget.setProperty(
                'visualContract',
                OPPORTUNITY_RISK_GROUP_VISUAL_CONTRACT,
            )
            group_state_label, group_state_tone = opportunity_risk_state_badge_contract(
                group.state
            )
            group_state_badge = MarketDEXStatusBadge(
                group_state_label,
                group_state_tone,
                group_widget,
            )
            group_state_badge.setProperty('opportunityRiskState', group.state)
            group_state_badge.setProperty(
                'opportunityRiskDisplayLabel',
                group_state_label,
            )
            evidence = QLabel(group.evidence_summary, group_widget)
            evidence.setObjectName('opportunityRiskEvidence')
            evidence.setWordWrap(True)
            source = QLabel(group.source_authority, group_widget)
            source.setObjectName('opportunityRiskSourceAuthority')
            source.setWordWrap(True)
            items = QWidget(group_widget)
            item_layout = QVBoxLayout(items)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(6)

            if group.items:
                for item in group.items:
                    item_label = QLabel(
                        (
                            f'{item.label}: {item.direction_label}. '
                            f'Why It Matters: {item.why_it_matters} '
                            f'Evidence: {item.evidence_summary} '
                            f'Source: {item.source_authority}. '
                            f'{item.freshness_label}.'
                        ),
                        items,
                    )
                    item_label.setObjectName('opportunityRiskItem')
                    item_label.setWordWrap(True)
                    item_label.setProperty('opportunityRiskKind', item.kind)
                    item_label.setProperty('opportunityRiskState', item.state)
                    item_label.setProperty('opportunityRiskCandidateKey', item.candidate_key)
                    item_label.setProperty(
                        'visualContract',
                        OPPORTUNITY_RISK_ITEM_VISUAL_CONTRACT,
                    )
                    item_layout.addWidget(item_label)
                    self.item_labels.append(item_label)
            else:
                empty_label = QLabel(
                    f'No prepared local {group.title} items.',
                    items,
                )
                empty_label.setObjectName('opportunityRiskEmptyGroup')
                empty_label.setWordWrap(True)
                empty_label.setProperty('opportunityRiskKind', group.kind)
                empty_label.setProperty('opportunityRiskState', group.state)
                item_layout.addWidget(empty_label)
                self.item_labels.append(empty_label)

            group_widget.add_header_action(group_state_badge)
            group_widget.add_content_widget(evidence)
            group_widget.add_content_widget(source)
            group_widget.add_content_widget(items)
            group_widget.setAccessibleName(
                f'Opportunity + Risk {group.title}. {group.state}. '
                f'{group.evidence_summary}. {group.source_authority}. '
                f'{group.freshness_label}'
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
        self.add_content_widget(self.headline_label)
        self.add_content_widget(self.error_label)
        self.add_content_widget(self.group_row)
        group_summary = '. '.join(
            f'{group.title}: {group.state}. {group.evidence_summary}'
            for group in self.view_model.groups
        )
        self.setAccessibleName(
            f'Opportunity + Risk. {self.view_model.headline}. {group_summary}'
        )
