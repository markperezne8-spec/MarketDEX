from pathlib import Path

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
from app.engines.mission_control.todays_top3 import (
    build_todays_top3_view_model,
    todays_top3_evidence,
)
from ui.capital_health_panel import CapitalHealthPanel
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import StatusTone
from ui.main_window import MainWindow

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CAPITAL_HEALTH_PANEL = REPOSITORY_ROOT / 'ui' / 'capital_health_panel.py'
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


def _metric(label: str, value_label: str, state: str = 'ready'):
    return capital_health_metric(
        label,
        state=state,
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
                    _metric('Available Cash', '$10 prepared value'),
                    _metric('Available for Redeployment', '$4 prepared value'),
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
                    _metric('Capital Recycling Rate', 'Prepared rate'),
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
                    _metric('Committed Capital', '$6 prepared value'),
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
                    _metric('Business-cycle Capital Growth', 'Prepared growth'),
                ),
            ),
        )
    )


def test_capital_health_panel_renders_injected_view_model_in_order():
    _application()
    model = _ready_capital_health_model()
    panel = CapitalHealthPanel(model)

    assert panel.title_label.text() == 'Capital Health'
    assert panel.description_label.text() == 'Read-only capital condition'
    assert panel.property('northStarTone') == NorthStarPanelTone.SCOREBOARD.value
    assert panel.property('dashboardRole') == 'capital-health-shell'
    assert panel.property('visualContract') == 'm1.16b-capital-health-shell'
    assert panel.property('capitalHealthState') == 'ready'
    assert panel.state_badge.text() == 'Ready'
    assert panel.state_badge.property('tone') == StatusTone.POSITIVE.value
    assert panel.headline_label.text() == 'Capital Health ready'
    assert panel.view_model is model
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Ready',
        'Ready',
        'Ready',
        'Ready',
    ]
    assert [label.text() for label in panel.metric_labels] == [
        'Available Cash: $10 prepared value — Available Cash prepared local evidence.',
        (
            'Available for Redeployment: $4 prepared value — '
            'Available for Redeployment prepared local evidence.'
        ),
        (
            'Capital Recycling Rate: Prepared rate — '
            'Capital Recycling Rate prepared local evidence.'
        ),
        'Committed Capital: $6 prepared value — Committed Capital prepared local evidence.',
        (
            'Business-cycle Capital Growth: Prepared growth — '
            'Business-cycle Capital Growth prepared local evidence.'
        ),
    ]


def test_capital_health_panel_renders_default_unavailable_state():
    _application()
    panel = CapitalHealthPanel()

    assert panel.state_badge.text() == 'Unavailable'
    assert panel.state_badge.property('tone') == StatusTone.WARNING.value
    assert panel.property('capitalHealthState') == 'unavailable'
    assert panel.headline_label.text() == 'Capital Health unavailable'
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Unavailable',
        'Unavailable',
        'Unavailable',
        'Unavailable',
    ]
    assert [label.text() for label in panel.group_labels][:5] == [
        'Availability',
        'Period unavailable',
        'Available Cash and Available for Redeployment evidence unavailable.',
        'Local evidence unavailable',
        (
            'Available Cash remains distinct from Available for Redeployment; '
            'neither value is inferred without prepared local evidence.'
        ),
    ]
    assert [label.text() for label in panel.metric_labels] == [
        'Available Cash: Unavailable — Evidence unavailable.',
        'Available for Redeployment: Unavailable — Evidence unavailable.',
        'Capital Recycling Rate: Unavailable — Evidence unavailable.',
        'Committed Capital: Unavailable — Evidence unavailable.',
        'Business-cycle Capital Growth: Unavailable — Evidence unavailable.',
    ]


def test_capital_health_panel_renders_error_safely_inline():
    _application()
    model = build_capital_health_view_model(
        evidence=(
            capital_health_group_evidence(
                'availability',
                state='ready',
                evidence_summary='Availability evidence is prepared locally.',
                source_authority='Prepared local capital evidence',
                period_label='Today',
                explanation='Available Cash and Available for Redeployment stay separate.',
                metrics=(
                    _metric('Available Cash', '$10 prepared value'),
                    _metric('Available for Redeployment', '$4 prepared value'),
                ),
            ),
        ),
        error_text='Prepared Capital Health evidence could not be read.',
    )
    panel = CapitalHealthPanel(model)

    assert panel.state_badge.text() == 'Error-safe'
    assert panel.state_badge.property('tone') == StatusTone.NEGATIVE.value
    assert panel.property('capitalHealthState') == 'error'
    assert panel.headline_label.text() == 'Capital Health unavailable'
    assert panel.error_label.text() == 'Prepared Capital Health evidence could not be read.'
    assert not panel.error_label.isHidden()
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Ready',
        'Unavailable',
        'Unavailable',
        'Unavailable',
    ]


def test_capital_health_group_cards_preserve_state_contract_properties():
    _application()
    model = build_capital_health_view_model(
        evidence=(
            capital_health_group_evidence(
                'availability',
                state='ready',
                evidence_summary='Availability evidence is prepared locally.',
                source_authority='Prepared local capital evidence',
                period_label='Today',
                explanation='Available Cash and Available for Redeployment stay separate.',
                metrics=(
                    _metric('Available Cash', '$10 prepared value'),
                    _metric('Available for Redeployment', '$4 prepared value'),
                ),
            ),
            capital_health_group_evidence(
                'recycling',
                state='partial',
                evidence_summary='Recycling evidence is partially prepared.',
                source_authority='Prepared local capital evidence',
                period_label='90 days',
                explanation='Formula authority is partially prepared.',
                metrics=(
                    _metric('Capital Recycling Rate', 'Partial', 'partial'),
                ),
            ),
            capital_health_group_evidence(
                'commitment',
                state='error',
                evidence_summary='Commitment evidence could not be assembled safely.',
                source_authority='Prepared local capital evidence',
                period_label='90 days',
                explanation='Committed capital is unavailable.',
                metrics=(
                    _metric('Committed Capital', 'Unavailable', 'error'),
                ),
            ),
        )
    )
    panel = CapitalHealthPanel(model)

    cards = [
        card for card in panel.findChildren(QWidget)
        if card.property('dashboardRole') == 'capital-health-group-card'
    ]

    assert [card.property('capitalHealthGroup') for card in cards] == [
        'availability',
        'recycling',
        'commitment',
        'growth',
    ]
    assert [card.property('capitalHealthState') for card in cards] == [
        'ready',
        'partial',
        'error',
        'unavailable',
    ]
    assert [
        card.property('visualContract') for card in cards
    ] == ['m1.16b-capital-health-group-card'] * 4
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Ready',
        'Partial',
        'Error-safe',
        'Unavailable',
    ]


def test_capital_health_panel_has_no_action_controls():
    _application()
    panel = CapitalHealthPanel(_ready_capital_health_model())

    assert panel.findChildren(QPushButton) == []


def test_capital_health_panel_uses_injected_model_without_fallback_builder(monkeypatch):
    _application()
    model = _ready_capital_health_model()

    def _blocked_default_builder():
        raise AssertionError('injected view model should not use the fallback builder')

    monkeypatch.setattr(
        'ui.capital_health_panel.build_capital_health_view_model',
        _blocked_default_builder,
    )

    panel = CapitalHealthPanel(model)

    assert panel.view_model is model
    assert panel.state_badge.text() == 'Ready'


def test_capital_health_panel_contract_has_no_runtime_side_effect_paths():
    source = CAPITAL_HEALTH_PANEL.read_text(encoding='utf-8')

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


def test_mission_control_wires_capital_health_only_from_prepared_view_model():
    source = MAIN_WINDOW.read_text(encoding='utf-8')

    assert 'CapitalHealthPanel(self._capital_health_view_model)' in source
    assert 'build_capital_health_view_model' not in source
    assert 'CapitalHealthViewModel | None = None' in source


def test_mission_control_places_capital_health_after_top3_before_dashboard_grid():
    _application()
    health_model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS'),
    )
    operational_model = _ready_operational_model()
    next_steps_model = _ready_next_steps_model()
    todays_top3_model = _ready_todays_top3_model()
    capital_health_model = _ready_capital_health_model()
    mission = _MissionControlService()
    window = MainWindow(
        mission,
        _InventoryService(),
        health_model,
        operational_model,
        next_steps_model,
        todays_top3_view_model=todays_top3_model,
        capital_health_view_model=capital_health_model,
    )

    layout = window.inventory_panel.layout()
    assert layout.itemAt(0).widget() is window.mission_control_header
    assert layout.itemAt(1).widget() is window.header_status_band
    assert layout.itemAt(2).widget() is window.health_status_card
    assert layout.itemAt(3).widget() is window.operational_status_strip
    assert layout.itemAt(4).widget() is window.next_steps_panel
    assert layout.itemAt(5).widget() is window.todays_top3_panel
    assert layout.itemAt(6).widget() is window.capital_health_panel
    assert layout.itemAt(7).widget() is window.dashboard_grid_shell
    assert window.capital_health_panel.view_model is capital_health_model

    old_panel = window.capital_health_panel
    window.refresh()
    assert window.capital_health_panel is old_panel
    assert mission.snapshot_calls == 2


def test_dashboard_grid_no_longer_contains_capital_health_placeholder():
    _application()
    window = MainWindow(_MissionControlService(), _InventoryService())

    placeholder_titles = [
        panel.title_label.text()
        for panel in window.dashboard_grid_shell.findChildren(QWidget)
        if panel.property('dashboardRole') == 'future-contract-placeholder'
        and hasattr(panel, 'title_label')
    ]

    assert 'Capital Health' not in placeholder_titles
    assert 'Opportunity + Risk' in placeholder_titles
