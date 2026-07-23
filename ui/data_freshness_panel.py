from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel

from app.engines.mission_control.data_freshness import (
    DATA_FRESHNESS_DOMAIN_ORDER,
    DataFreshnessState,
    DataFreshnessViewModel,
    build_data_freshness_view_model,
)
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import (
    MarketDEXDashboardPanel,
    MarketDEXStatusBadge,
    StatusTone,
)


DATA_FRESHNESS_VISUAL_CONTRACT = 'm1.20b-data-freshness-shell'
DATA_FRESHNESS_DOMAIN_VISUAL_CONTRACT = 'm1.20b-data-freshness-domain-shell'

DATA_FRESHNESS_STATE_LABELS: dict[DataFreshnessState, tuple[str, StatusTone]] = {
    'ready': ('Ready', StatusTone.POSITIVE),
    'unavailable': ('Unavailable', StatusTone.WARNING),
    'partial': ('Partial', StatusTone.WARNING),
    'error': ('Error-safe', StatusTone.NEGATIVE),
}


def data_freshness_state_badge_contract(
    state: DataFreshnessState,
) -> tuple[str, StatusTone]:
    try:
        return DATA_FRESHNESS_STATE_LABELS[state]
    except KeyError as exc:
        raise ValueError('unsupported Data Freshness display state') from exc


class DataFreshnessPanel(MarketDEXDashboardPanel):
    """Compact read-only surface for explicit evidence freshness states."""

    def __init__(
        self,
        view_model: DataFreshnessViewModel | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            'Data Freshness',
            'Read-only evidence recency and authority status',
            parent,
            tone=NorthStarPanelTone.INTELLIGENCE,
        )
        self.view_model = view_model or build_data_freshness_view_model()
        self.setObjectName('marketdexDashboardPanel')
        self.setProperty('dashboardRole', 'data-freshness-shell')
        self.setProperty('visualContract', DATA_FRESHNESS_VISUAL_CONTRACT)
        self.setProperty('dataFreshnessState', self.view_model.state)
        self.setProperty(
            'dataFreshnessDomainOrder',
            ','.join(DATA_FRESHNESS_DOMAIN_ORDER),
        )

        state_label, state_tone = data_freshness_state_badge_contract(
            self.view_model.state
        )
        self.state_badge = MarketDEXStatusBadge(
            state_label,
            state_tone,
            self.content_widget,
        )
        self.add_header_action(self.state_badge)

        self.headline_label = QLabel(self.view_model.headline, self.content_widget)
        self.headline_label.setObjectName('dataFreshnessHeadline')
        self.headline_label.setWordWrap(True)
        self.add_content_widget(self.headline_label)

        self.error_label = QLabel(
            self.view_model.error_text or '',
            self.content_widget,
        )
        self.error_label.setObjectName('dataFreshnessErrorText')
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(self.view_model.state == 'error')
        self.add_content_widget(self.error_label)

        self.domain_grid = QGridLayout()
        self.domain_grid.setContentsMargins(0, 0, 0, 0)
        self.domain_grid.setHorizontalSpacing(10)
        self.domain_grid.setVerticalSpacing(8)
        self.domain_widgets: list[MarketDEXDashboardPanel] = []

        for index, domain in enumerate(self.view_model.domains):
            domain_widget = MarketDEXDashboardPanel(
                domain.title,
                domain.source_authority,
                self.content_widget,
                tone=NorthStarPanelTone.SCOREBOARD,
            )
            domain_widget.setObjectName('marketdexDashboardPanel')
            domain_widget.setProperty('dashboardRole', 'data-freshness-domain-shell')
            domain_widget.setProperty('dataFreshnessDomain', domain.domain)
            domain_widget.setProperty('dataFreshnessState', domain.state)
            domain_widget.setProperty(
                'visualContract',
                DATA_FRESHNESS_DOMAIN_VISUAL_CONTRACT,
            )

            domain_label, domain_tone = data_freshness_state_badge_contract(
                domain.state
            )
            domain_widget.add_header_action(
                MarketDEXStatusBadge(domain_label, domain_tone, domain_widget)
            )

            as_of = QLabel(domain.as_of_label, domain_widget)
            as_of.setObjectName('dataFreshnessAsOf')
            as_of.setWordWrap(True)
            freshness = QLabel(domain.freshness_label, domain_widget)
            freshness.setObjectName('dataFreshnessLabel')
            freshness.setWordWrap(True)
            detail = QLabel(domain.detail, domain_widget)
            detail.setObjectName('dataFreshnessDetail')
            detail.setWordWrap(True)

            domain_widget.add_content_widget(as_of)
            domain_widget.add_content_widget(freshness)
            domain_widget.add_content_widget(detail)
            domain_widget.setAccessibleName(
                f'Data Freshness {domain.title}. {domain_label}. '
                f'{domain.source_authority}. {domain.as_of_label}. '
                f'{domain.freshness_label}. {domain.detail}'
            )
            self.domain_widgets.append(domain_widget)
            self.domain_grid.addWidget(domain_widget, index // 2, index % 2)

        self.content_layout.addLayout(self.domain_grid)
        domain_summary = '. '.join(
            f'{domain.title}: {domain.state}. {domain.detail}'
            for domain in self.view_model.domains
        )
        self.setAccessibleName(
            f'Data Freshness. {self.view_model.headline}. {domain_summary}'
        )
