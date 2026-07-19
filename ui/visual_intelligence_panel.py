from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from app.engines.mission_control.visual_intelligence import (
    VISUAL_INTELLIGENCE_REGION_ORDER,
    VisualIntelligenceState,
    VisualIntelligenceViewModel,
    build_visual_intelligence_view_model,
)
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXStatusBadge,
    StatusTone,
)


VISUAL_INTELLIGENCE_VISUAL_CONTRACT = 'm1.19b-visual-intelligence-shell'
VISUAL_INTELLIGENCE_REGION_VISUAL_CONTRACT = (
    'm1.19b-visual-intelligence-region-shell'
)

VISUAL_INTELLIGENCE_STATE_LABELS: dict[
    VisualIntelligenceState, tuple[str, StatusTone]
] = {
    'ready': ('Ready', StatusTone.POSITIVE),
    'unavailable': ('Unavailable', StatusTone.WARNING),
    'partial': ('Partial', StatusTone.WARNING),
    'error': ('Error-safe', StatusTone.NEGATIVE),
}


def visual_intelligence_state_badge_contract(
    state: VisualIntelligenceState,
) -> tuple[str, StatusTone]:
    try:
        return VISUAL_INTELLIGENCE_STATE_LABELS[state]
    except KeyError as exc:
        raise ValueError('unsupported Visual Intelligence display state') from exc


class VisualIntelligencePanel(MarketDEXDashboardPanel):
    """Read-only Visual Intelligence contract-backed surface."""

    def __init__(
        self,
        view_model: VisualIntelligenceViewModel | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            'Visual Intelligence',
            'Read-only visual intelligence and alert-region shell',
            parent,
            tone=NorthStarPanelTone.INTELLIGENCE,
        )
        self.view_model = view_model or build_visual_intelligence_view_model()
        self.setObjectName('marketdexDashboardPanel')
        self.setProperty('dashboardRole', 'visual-intelligence-shell')
        self.setProperty('visualContract', VISUAL_INTELLIGENCE_VISUAL_CONTRACT)
        self.setProperty('visualIntelligenceState', self.view_model.state)
        self.setProperty(
            'visualIntelligenceRegionOrder',
            ','.join(VISUAL_INTELLIGENCE_REGION_ORDER),
        )

        state_label, state_tone = visual_intelligence_state_badge_contract(
            self.view_model.state
        )
        self.state_badge = MarketDEXStatusBadge(
            state_label,
            state_tone,
            self.content_widget,
        )
        self.state_badge.setProperty(
            'visualIntelligenceState',
            self.view_model.state,
        )
        self.state_badge.setProperty(
            'visualIntelligenceDisplayLabel',
            state_label,
        )

        self.headline_label = QLabel(
            self.view_model.headline,
            self.content_widget,
        )
        self.headline_label.setObjectName('visualIntelligenceHeadline')
        self.headline_label.setWordWrap(True)

        self.error_label = QLabel(
            self.view_model.error_text or '',
            self.content_widget,
        )
        self.error_label.setObjectName('visualIntelligenceErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')

        self.region_grid = QGridLayout()
        self.region_grid.setContentsMargins(0, 0, 0, 0)
        self.region_grid.setHorizontalSpacing(10)
        self.region_grid.setVerticalSpacing(8)
        self.region_widgets: list[MarketDEXDashboardPanel] = []

        for index, region in enumerate(self.view_model.regions):
            region_widget = MarketDEXDashboardPanel(
                region.title,
                region.subtitle,
                self.content_widget,
                tone=NorthStarPanelTone.SCOREBOARD,
            )
            region_widget.setObjectName('marketdexDashboardPanel')
            region_widget.setProperty(
                'dashboardRole',
                'visual-intelligence-region-shell',
            )
            region_widget.setProperty(
                'visualIntelligenceRegion',
                region.region,
            )
            region_widget.setProperty(
                'visualIntelligenceState',
                region.state,
            )
            region_widget.setProperty(
                'visualContract',
                VISUAL_INTELLIGENCE_REGION_VISUAL_CONTRACT,
            )

            region_state_label, region_state_tone = (
                visual_intelligence_state_badge_contract(region.state)
            )
            region_badge = MarketDEXStatusBadge(
                region_state_label,
                region_state_tone,
                region_widget,
            )
            region_badge.setProperty(
                'visualIntelligenceRegion',
                region.region,
            )
            region_badge.setProperty(
                'visualIntelligenceDisplayLabel',
                region_state_label,
            )

            evidence = QLabel(region.evidence_summary, region_widget)
            evidence.setObjectName('visualIntelligenceEvidence')
            evidence.setWordWrap(True)
            source = QLabel(region.source_authority, region_widget)
            source.setObjectName('visualIntelligenceSourceAuthority')
            source.setWordWrap(True)
            freshness = QLabel(region.freshness_label, region_widget)
            freshness.setObjectName('visualIntelligenceFreshness')
            freshness.setWordWrap(True)
            detail = QLabel(region.detail, region_widget)
            detail.setObjectName('visualIntelligenceDetail')
            detail.setWordWrap(True)

            region_widget.add_header_action(region_badge)
            region_widget.add_content_widget(evidence)
            region_widget.add_content_widget(source)
            region_widget.add_content_widget(freshness)
            region_widget.add_content_widget(detail)
            region_widget.setAccessibleName(
                f'Visual Intelligence {region.title}. '
                f'{region_state_label}. {region.evidence_summary}. '
                f'{region.source_authority}. {region.freshness_label}. '
                f'{region.detail}'
            )
            self.region_widgets.append(region_widget)
            self.region_grid.addWidget(region_widget, index // 2, index % 2)

        self.add_content_widget(self.state_badge)
        self.add_content_widget(self.headline_label)
        self.add_content_widget(self.error_label)
        self.content_layout.addLayout(self.region_grid)
        region_summary = '. '.join(
            f'{region.title}: {region.state}. {region.evidence_summary}'
            for region in self.view_model.regions
        )
        self.setAccessibleName(
            f'Visual Intelligence. {self.view_model.headline}. {region_summary}'
        )
