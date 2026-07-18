from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from app.engines.health.status_view_model import build_health_status_view_model
from app.engines.mission_control.capital_health import (
    build_capital_health_view_model,
    capital_health_group_evidence,
    capital_health_metric,
)
from app.engines.mission_control.next_steps import (
    build_next_step_readiness_view_model,
    next_step_readiness_evidence,
)
from app.engines.mission_control.operational_status import (
    build_operational_status_view_model,
    operational_status_evidence,
)
from app.engines.mission_control.opportunity_risk import (
    OPPORTUNITY_RISK_KIND_ORDER,
    build_opportunity_risk_view_model,
    opportunity_risk_evidence,
)
from app.engines.mission_control.todays_top3 import (
    build_todays_top3_view_model,
    todays_top3_evidence,
)
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import StatusTone
from ui.main_window import MainWindow
from ui.opportunity_risk_panel import (
    OPPORTUNITY_RISK_GROUP_VISUAL_CONTRACT,
    OPPORTUNITY_RISK_ITEM_VISUAL_CONTRACT,
    OPPORTUNITY_RISK_VISUAL_CONTRACT,
    OpportunityRiskPanel,
    opportunity_risk_state_badge_contract,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OPPORTUNITY_RISK_PANEL = REPOSITORY_ROOT / 'ui' / 'opportunity_risk_panel.py'
MAIN_WINDOW = REPOSITORY_ROOT / 'ui' / 'main_window.py'


def _application():
    return QApplication.instance() or QApplication([])


class _MissionControlService:
    def __init__(self):
        self.snapshot_calls = 0

    def snapshot(self):
        self.snapshot_calls += 1
        return {
            'inventory_units': 0,
            'inventory_asset_count': 0,
            'inventory_cost_minor': 0,
            'completed_sales': 0,
            'revenue_minor': 0,
            'profit_minor': 0,
            'verified_audits': 0,
            'authority_events': 0,
            'database_path': 'contract-test.sqlite3',
        }


class _InventoryService:
    def list_inventory(self, **_kwargs):
        return []

    def list_archived_inventory(self, **_kwargs):
        return []

    def summarize_inventory(self, _rows):
        return {
            'asset_count': 0,
            'total_units': 0,
            'total_cost_minor': 0,
        }


def _ready_operational_model():
    return build_operational_status_view_model(
        evidence=(
            operational_status_evidence(
                'local_authority',
                state='available',
                detail='Local runtime authority is present.',
            ),
            operational_status_evidence(
                'offline_first',
                state='available',
                detail='No network evidence is required.',
            ),
            operational_status_evidence(
                'inventory',
                state='available',
                detail='Inventory snapshot is locally available.',
            ),
            operational_status_evidence(
                'audit_authority',
                state='available',
                detail='Verified audit evidence is present.',
            ),
        )
    )


def _ready_next_steps_model():
    return build_next_step_readiness_view_model(
        evidence=(
            next_step_readiness_evidence(
                'next_safe_action',
                state='ready',
                detail='Prepare the next local inventory review.',
            ),
            next_step_readiness_evidence(
                'inventory_readiness',
                state='ready',
                detail='Inventory summary is prepared locally.',
            ),
            next_step_readiness_evidence(
                'authority_audit_readiness',
                state='ready',
                detail='Authority evidence is prepared locally.',
            ),
            next_step_readiness_evidence(
                'readiness_note',
                state='ready',
                detail='No action has been started.',
            ),
        )
    )


def _ready_todays_top3_model():
    return build_todays_top3_view_model(
        evidence=(
            todays_top3_evidence(
                1,
                state='ready',
                title='Review listing readiness',
                reason='Listing readiness evidence is prepared locally.',
                evidence_summary='Inventory listing blockers are available.',
                affected_area='Listing',
                next_safe_preparation='Prepare local listing review.',
            ),
            todays_top3_evidence(
                2,
                state='ready',
                title='Review inventory age',
                reason='Inventory age evidence is prepared locally.',
                evidence_summary='Inventory age rows are available.',
                affected_area='Inventory',
                next_safe_preparation='Prepare inventory age review.',
            ),
            todays_top3_evidence(
                3,
                state='ready',
                title='Review audit coverage',
                reason='Audit evidence is prepared locally.',
                evidence_summary='Authority events are available.',
                affected_area='Authority',
                next_safe_preparation='Prepare audit coverage review.',
            ),
        )
    )


def _capital_metric(label: str, value_label: str):
    return capital_health_metric(
        label,
        state='ready',
        value_label=value_label,
        evidence_summary=f'{label} prepared local evidence.',
    )


def _ready_capital_health_model():
    return build_capital_health_view_model(
        evidence=(
            capital_health_group_evidence(
                'availability',
                state='ready',
                evidence_summary='Availability evidence is prepared locally.',
                source_authority='Prepared local capital evidence',
                period_label='Today',
                explanation='Available Cash and Available for Redeployment stay separate.',
                metrics=(
                    _capital_metric('Available Cash', '$10 prepared value'),
                    _capital_metric('Available for Redeployment', '$4 prepared value'),
                ),
            ),
            capital_health_group_evidence(
                'recycling',
                state='ready',
                evidence_summary='Recycling evidence is prepared locally.',
                source_authority='Prepared local capital evidence',
                period_label='90 days',
                explanation='Formula authority is prepared locally.',
                metrics=(
                    _capital_metric('Capital Recycling Rate', 'Prepared rate'),
                ),
            ),
            capital_health_group_evidence(
                'commitment',
                state='ready',
                evidence_summary='Commitment evidence is prepared locally.',
                source_authority='Prepared local capital evidence',
                period_label='90 days',
                explanation='Committed capital is read-only.',
                metrics=(
                    _capital_metric('Committed Capital', '$6 prepared value'),
                ),
            ),
            capital_health_group_evidence(
                'growth',
                state='ready',
                evidence_summary='Growth evidence is prepared locally.',
                source_authority='Prepared local capital evidence',
                period_label='90 days',
                explanation='Growth excludes external cash injection.',
                metrics=(
                    _capital_metric('Business-cycle Capital Growth', 'Prepared growth'),
                ),
            ),
        )
    )


def _opportunity_risk_item(
    kind: str,
    display_order: int,
    candidate_key: str,
    *,
    state: str = 'ready',
):
    return opportunity_risk_evidence(
        kind,
        state=state,
        display_order=display_order,
        candidate_key=candidate_key,
        label=f'{kind} {display_order}',
        why_it_matters=f'{kind} {display_order} may change if Mark waits.',
        direction_label=f'{kind} condition',
        evidence_summary=f'{kind} {display_order} prepared local evidence.',
        source_authority='Prepared local evidence',
        freshness_label='As of prepared local snapshot',
    )


def _ready_opportunity_risk_model():
    return build_opportunity_risk_view_model(
        evidence=(
            _opportunity_risk_item('opportunity', 1, 'opportunity-a'),
            _opportunity_risk_item('risk', 1, 'risk-a'),
        )
    )


def test_opportunity_risk_panel_renders_injected_view_model_in_order():
    _application()
    model = _ready_opportunity_risk_model()
    panel = OpportunityRiskPanel(model)

    assert panel.title_label.text() == 'Opportunity + Risk'
    assert panel.description_label.text() == 'Read-only situational awareness'
    assert panel.property('northStarTone') == NorthStarPanelTone.SCOREBOARD.value
    assert panel.property('dashboardRole') == 'opportunity-risk-shell'
    assert panel.property('visualContract') == OPPORTUNITY_RISK_VISUAL_CONTRACT
    assert panel.property('opportunityRiskState') == 'ready'
    assert panel.property('opportunityRiskGroupOrder') == ','.join(
        OPPORTUNITY_RISK_KIND_ORDER
    )
    assert panel.state_badge.text() == 'Ready'
    assert panel.state_badge.property('tone') == StatusTone.POSITIVE.value
    assert panel.state_badge.property('opportunityRiskState') == 'ready'
    assert panel.state_badge.property('opportunityRiskDisplayLabel') == 'Ready'
    assert panel.headline_label.text() == 'Opportunity + Risk ready'
    assert panel.view_model is model
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Ready',
        'Ready',
    ]
    assert [label.text() for label in panel.group_labels] == [
        'Opportunities',
        'Prepared local freshness',
        'Opportunities prepared local evidence.',
        'Prepared local evidence',
        'Risks',
        'Prepared local freshness',
        'Risks prepared local evidence.',
        'Prepared local evidence',
    ]
    assert [label.property('visualContract') for label in panel.item_labels] == [
        OPPORTUNITY_RISK_ITEM_VISUAL_CONTRACT,
        OPPORTUNITY_RISK_ITEM_VISUAL_CONTRACT,
    ]
    assert [label.property('opportunityRiskDisplayLabel') for label in panel.item_labels] == [
        'Ready',
        'Ready',
    ]
    assert [label.property('opportunityRiskStateTone') for label in panel.item_labels] == [
        StatusTone.POSITIVE.value,
        StatusTone.POSITIVE.value,
    ]
    assert [label.property('opportunityRiskCandidateKey') for label in panel.item_labels] == [
        'opportunity-a',
        'risk-a',
    ]


def test_opportunity_risk_panel_renders_default_unavailable_state():
    _application()
    panel = OpportunityRiskPanel()

    assert panel.state_badge.text() == 'Unavailable'
    assert panel.state_badge.property('tone') == StatusTone.WARNING.value
    assert panel.state_badge.property('opportunityRiskState') == 'unavailable'
    assert panel.state_badge.property('opportunityRiskDisplayLabel') == 'Unavailable'
    assert panel.property('opportunityRiskState') == 'unavailable'
    assert panel.headline_label.text() == 'Opportunity + Risk unavailable'
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Unavailable',
        'Unavailable',
    ]
    assert [label.text() for label in panel.group_labels] == [
        'Opportunities',
        'Freshness unavailable',
        'Prepared local Opportunity evidence unavailable.',
        'Local evidence unavailable',
        'Risks',
        'Freshness unavailable',
        'Prepared local Risk evidence unavailable.',
        'Local evidence unavailable',
    ]
    assert [label.text() for label in panel.item_labels] == [
        'Unavailable - No prepared local Opportunities items.',
        'Unavailable - No prepared local Risks items.',
    ]
    assert [label.property('opportunityRiskDisplayLabel') for label in panel.item_labels] == [
        'Unavailable',
        'Unavailable',
    ]
    assert [label.property('opportunityRiskStateTone') for label in panel.item_labels] == [
        StatusTone.WARNING.value,
        StatusTone.WARNING.value,
    ]


def test_opportunity_risk_panel_renders_error_safely_inline():
    _application()
    model = build_opportunity_risk_view_model(
        evidence=(
            _opportunity_risk_item('opportunity', 1, 'opportunity-a'),
            _opportunity_risk_item('risk', 1, 'risk-a'),
        ),
        error_text='Prepared Opportunity + Risk evidence could not be read.',
    )
    panel = OpportunityRiskPanel(model)

    assert panel.state_badge.text() == 'Error-safe'
    assert panel.state_badge.property('tone') == StatusTone.NEGATIVE.value
    assert panel.state_badge.property('opportunityRiskState') == 'error'
    assert panel.state_badge.property('opportunityRiskDisplayLabel') == 'Error-safe'
    assert panel.property('opportunityRiskState') == 'error'
    assert panel.headline_label.text() == 'Opportunity + Risk unavailable'
    assert panel.error_label.text() == 'Prepared Opportunity + Risk evidence could not be read.'
    assert not panel.error_label.isHidden()


def test_opportunity_risk_group_cards_preserve_state_contract_properties():
    _application()
    model = build_opportunity_risk_view_model(
        evidence=(
            _opportunity_risk_item('opportunity', 1, 'opportunity-a'),
            opportunity_risk_evidence(
                'risk',
                state='partial',
                display_order=1,
                candidate_key='risk-a',
                label='risk 1',
                why_it_matters='risk 1 may change if Mark waits.',
                direction_label='risk condition',
                evidence_summary='risk 1 prepared local evidence.',
                source_authority='Prepared local evidence',
                freshness_label='As of prepared local snapshot',
            ),
        )
    )
    panel = OpportunityRiskPanel(model)

    cards = [
        card for card in panel.findChildren(QWidget)
        if card.property('dashboardRole') == 'opportunity-risk-group-card'
    ]

    assert [card.property('opportunityRiskKind') for card in cards] == [
        'opportunity',
        'risk',
    ]
    assert [card.property('opportunityRiskState') for card in cards] == [
        'ready',
        'partial',
    ]
    assert [card.property('visualContract') for card in cards] == [
        OPPORTUNITY_RISK_GROUP_VISUAL_CONTRACT,
        OPPORTUNITY_RISK_GROUP_VISUAL_CONTRACT,
    ]
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Ready',
        'Partial',
    ]


def test_opportunity_risk_items_preserve_each_display_state_contract():
    _application()
    model = build_opportunity_risk_view_model(
        evidence=(
            _opportunity_risk_item(
                'opportunity',
                1,
                'opportunity-ready',
                state='ready',
            ),
            _opportunity_risk_item(
                'opportunity',
                2,
                'opportunity-partial',
                state='partial',
            ),
            _opportunity_risk_item(
                'risk',
                1,
                'risk-unavailable',
                state='unavailable',
            ),
            _opportunity_risk_item(
                'risk',
                2,
                'risk-error',
                state='error',
            ),
        )
    )
    panel = OpportunityRiskPanel(model)

    assert [label.property('opportunityRiskCandidateKey') for label in panel.item_labels] == [
        'opportunity-ready',
        'opportunity-partial',
        'risk-unavailable',
        'risk-error',
    ]
    assert [label.property('opportunityRiskState') for label in panel.item_labels] == [
        'ready',
        'partial',
        'unavailable',
        'error',
    ]
    assert [label.property('opportunityRiskDisplayLabel') for label in panel.item_labels] == [
        'Ready',
        'Partial',
        'Unavailable',
        'Error-safe',
    ]
    assert [label.property('opportunityRiskStateTone') for label in panel.item_labels] == [
        StatusTone.POSITIVE.value,
        StatusTone.WARNING.value,
        StatusTone.WARNING.value,
        StatusTone.NEGATIVE.value,
    ]
    assert [label.text().split(' - ', 1)[0] for label in panel.item_labels] == [
        'Ready',
        'Partial',
        'Unavailable',
        'Error-safe',
    ]
    assert [
        label.property('visualContract') for label in panel.item_labels
    ] == [OPPORTUNITY_RISK_ITEM_VISUAL_CONTRACT] * 4


@pytest.mark.parametrize(
    ('state', 'label', 'tone'),
    [
        ('ready', 'Ready', StatusTone.POSITIVE),
        ('unavailable', 'Unavailable', StatusTone.WARNING),
        ('partial', 'Partial', StatusTone.WARNING),
        ('error', 'Error-safe', StatusTone.NEGATIVE),
    ],
)
def test_opportunity_risk_state_badge_contract_is_locked(state, label, tone):
    assert opportunity_risk_state_badge_contract(state) == (label, tone)


def test_opportunity_risk_state_badge_contract_rejects_unknown_state():
    with pytest.raises(ValueError):
        opportunity_risk_state_badge_contract('live')


def test_opportunity_risk_panel_has_no_action_controls():
    _application()
    panel = OpportunityRiskPanel(_ready_opportunity_risk_model())

    assert panel.findChildren(QPushButton) == []


def test_opportunity_risk_panel_uses_injected_model_without_fallback_builder(monkeypatch):
    _application()
    model = _ready_opportunity_risk_model()

    def _blocked_default_builder():
        raise AssertionError('injected view model should not use the fallback builder')

    monkeypatch.setattr(
        'ui.opportunity_risk_panel.build_opportunity_risk_view_model',
        _blocked_default_builder,
    )

    panel = OpportunityRiskPanel(model)

    assert panel.view_model is model
    assert panel.state_badge.text() == 'Ready'


def test_opportunity_risk_panel_contract_has_no_runtime_side_effect_paths():
    source = OPPORTUNITY_RISK_PANEL.read_text(encoding='utf-8')

    prohibited_tokens = (
        'QMessageBox',
        'QDialog',
        'QTimer',
        'socket',
        'requests',
        'urllib',
        'sqlite3',
        'open(',
        'Path(',
        'threading',
        'schedule',
        'poll',
        'database',
        'persist',
        'save',
        'mutation',
        'import_inventory',
        'export_inventory',
        'add_asset',
        'adjust_asset',
        'archive_asset',
        'restore_asset',
    )

    for token in prohibited_tokens:
        assert token not in source


def test_mission_control_wires_opportunity_risk_only_from_prepared_view_model():
    source = MAIN_WINDOW.read_text(encoding='utf-8')

    assert 'OpportunityRiskPanel(self._opportunity_risk_view_model)' in source
    assert 'build_opportunity_risk_view_model' not in source
    assert 'OpportunityRiskViewModel | None = None' in source


def test_mission_control_places_opportunity_risk_after_capital_health_before_dashboard_grid():
    _application()
    health_model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS'),
    )
    mission = _MissionControlService()
    opportunity_risk_model = _ready_opportunity_risk_model()
    window = MainWindow(
        mission,
        _InventoryService(),
        health_model,
        _ready_operational_model(),
        _ready_next_steps_model(),
        todays_top3_view_model=_ready_todays_top3_model(),
        capital_health_view_model=_ready_capital_health_model(),
        opportunity_risk_view_model=opportunity_risk_model,
    )

    layout = window.inventory_panel.layout()
    assert layout.itemAt(0).widget() is window.mission_control_header
    assert layout.itemAt(1).widget() is window.header_status_band
    assert layout.itemAt(2).widget() is window.health_status_card
    assert layout.itemAt(3).widget() is window.operational_status_strip
    assert layout.itemAt(4).widget() is window.next_steps_panel
    assert layout.itemAt(5).widget() is window.todays_top3_panel
    assert layout.itemAt(6).widget() is window.capital_health_panel
    assert layout.itemAt(7).widget() is window.opportunity_risk_panel
    assert layout.itemAt(8).widget() is window.dashboard_grid_shell
    assert window.opportunity_risk_panel.view_model is opportunity_risk_model

    old_panel = window.opportunity_risk_panel
    window.refresh()
    assert window.opportunity_risk_panel is old_panel
    assert mission.snapshot_calls == 2


def test_dashboard_grid_no_longer_contains_opportunity_risk_placeholder():
    _application()
    window = MainWindow(_MissionControlService(), _InventoryService())

    placeholder_titles = [
        panel.title_label.text()
        for panel in window.dashboard_grid_shell.findChildren(QWidget)
        if panel.property('dashboardRole') == 'future-contract-placeholder'
        and hasattr(panel, 'title_label')
    ]

    assert 'Opportunity + Risk' not in placeholder_titles
