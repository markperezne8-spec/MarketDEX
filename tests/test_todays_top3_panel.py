from pathlib import Path

from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from app.engines.health.status_view_model import build_health_status_view_model
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
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import StatusTone
from ui.main_window import MainWindow
from ui.todays_top3_panel import TodaysTop3Panel

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TODAYS_TOP3_PANEL = REPOSITORY_ROOT / 'ui' / 'todays_top3_panel.py'
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


def test_todays_top3_panel_renders_injected_view_model_in_order():
    _application()
    model = _ready_todays_top3_model()
    panel = TodaysTop3Panel(model)

    assert panel.title_label.text() == "Today's Top 3"
    assert panel.description_label.text() == 'Read-only attention priorities'
    assert panel.property('northStarTone') == NorthStarPanelTone.COMMAND.value
    assert panel.property('dashboardRole') == 'todays-top3-shell'
    assert panel.property('visualContract') == 'm1.15c-todays-top3-display-states'
    assert panel.property('attentionState') == 'ready'
    assert panel.state_badge.text() == 'Ready'
    assert panel.state_badge.property('tone') == StatusTone.POSITIVE.value
    assert panel.headline_label.text() == "Today's Top 3 ready"
    assert panel.view_model is model
    assert [badge.text() for badge in panel.item_state_badges] == [
        'Ready',
        'Ready',
        'Ready',
    ]
    assert [
        badge.property('tone') for badge in panel.item_state_badges
    ] == [StatusTone.POSITIVE.value] * 3
    assert [label.text() for label in panel.item_labels] == [
        '#1 Review listing readiness',
        'Listing',
        'Listing readiness evidence is prepared locally.',
        'Inventory listing blockers are available.',
        'Prepare local listing review.',
        '#2 Review inventory age',
        'Inventory',
        'Inventory age evidence is prepared locally.',
        'Inventory age rows are available.',
        'Prepare inventory age review.',
        '#3 Review audit coverage',
        'Authority',
        'Audit evidence is prepared locally.',
        'Authority events are available.',
        'Prepare audit coverage review.',
    ]


def test_todays_top3_panel_renders_default_unavailable_state():
    _application()
    panel = TodaysTop3Panel()

    assert panel.state_badge.text() == 'Unavailable'
    assert panel.state_badge.property('tone') == StatusTone.WARNING.value
    assert panel.property('attentionState') == 'unavailable'
    assert panel.headline_label.text() == "Today's Top 3 unavailable"
    assert [badge.text() for badge in panel.item_state_badges] == [
        'Unavailable',
        'Unavailable',
        'Unavailable',
    ]
    assert [
        badge.property('tone') for badge in panel.item_state_badges
    ] == [StatusTone.WARNING.value] * 3
    assert [label.text() for label in panel.item_labels] == [
        '#1 Priority 1 unavailable',
        'Unassigned',
        'Evidence unavailable.',
        'Evidence unavailable.',
        'No safe local preparation available.',
        '#2 Priority 2 unavailable',
        'Unassigned',
        'Evidence unavailable.',
        'Evidence unavailable.',
        'No safe local preparation available.',
        '#3 Priority 3 unavailable',
        'Unassigned',
        'Evidence unavailable.',
        'Evidence unavailable.',
        'No safe local preparation available.',
    ]


def test_todays_top3_panel_renders_partial_state_without_inventing_evidence():
    _application()
    model = build_todays_top3_view_model(
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
                state='partial',
                title='Review inventory age',
                reason='Some inventory age evidence is missing.',
                evidence_summary='Inventory age rows are partially available.',
                affected_area='Inventory',
                next_safe_preparation='Prepare inventory age review.',
            ),
        )
    )
    panel = TodaysTop3Panel(model)

    assert panel.state_badge.text() == 'Partial'
    assert panel.state_badge.property('tone') == StatusTone.WARNING.value
    assert panel.property('attentionState') == 'partial'
    assert panel.headline_label.text() == "Today's Top 3 partially available"
    assert [badge.text() for badge in panel.item_state_badges] == [
        'Ready',
        'Partial',
        'Unavailable',
    ]
    assert [badge.property('tone') for badge in panel.item_state_badges] == [
        StatusTone.POSITIVE.value,
        StatusTone.WARNING.value,
        StatusTone.WARNING.value,
    ]


def test_todays_top3_panel_renders_error_safely_inline():
    _application()
    model = build_todays_top3_view_model(
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
        ),
        error_text="Prepared Today's Top 3 evidence could not be read.",
    )
    panel = TodaysTop3Panel(model)

    assert panel.state_badge.text() == 'Error-safe'
    assert panel.state_badge.property('tone') == StatusTone.NEGATIVE.value
    assert panel.property('attentionState') == 'error'
    assert panel.headline_label.text() == "Today's Top 3 unavailable"
    assert panel.error_label.text() == (
        "Prepared Today's Top 3 evidence could not be read."
    )
    assert not panel.error_label.isHidden()
    assert [badge.text() for badge in panel.item_state_badges] == [
        'Ready',
        'Unavailable',
        'Unavailable',
    ]
    assert [badge.property('tone') for badge in panel.item_state_badges] == [
        StatusTone.POSITIVE.value,
        StatusTone.WARNING.value,
        StatusTone.WARNING.value,
    ]


def test_todays_top3_priority_cards_preserve_state_contract_properties():
    _application()
    model = build_todays_top3_view_model(
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
                state='partial',
                title='Review inventory age',
                reason='Some inventory age evidence is missing.',
                evidence_summary='Inventory age rows are partially available.',
                affected_area='Inventory',
                next_safe_preparation='Prepare inventory age review.',
            ),
            todays_top3_evidence(
                3,
                state='error',
                title='Review audit coverage',
                reason='Audit evidence could not be assembled safely.',
                evidence_summary='Authority evidence is unavailable.',
                affected_area='Authority',
                next_safe_preparation='Pause until audit evidence is available.',
            ),
        )
    )
    panel = TodaysTop3Panel(model)

    cards = [
        card for card in panel.findChildren(QWidget)
        if card.property('dashboardRole') == 'todays-top3-priority-card'
    ]

    assert [card.property('priorityRank') for card in cards] == [1, 2, 3]
    assert [card.property('attentionState') for card in cards] == [
        'ready',
        'partial',
        'error',
    ]
    assert [
        card.property('visualContract') for card in cards
    ] == ['m1.15c-todays-top3-priority-card-state'] * 3
    assert [badge.text() for badge in panel.item_state_badges] == [
        'Ready',
        'Partial',
        'Error-safe',
    ]
    assert [badge.property('tone') for badge in panel.item_state_badges] == [
        StatusTone.POSITIVE.value,
        StatusTone.WARNING.value,
        StatusTone.NEGATIVE.value,
    ]


def test_todays_top3_panel_has_no_action_controls():
    _application()
    panel = TodaysTop3Panel(_ready_todays_top3_model())

    assert panel.findChildren(QPushButton) == []


def test_todays_top3_panel_uses_injected_model_without_fallback_builder(monkeypatch):
    _application()
    model = _ready_todays_top3_model()

    def _blocked_default_builder():
        raise AssertionError('injected view model should not use the fallback builder')

    monkeypatch.setattr(
        'ui.todays_top3_panel.build_todays_top3_view_model',
        _blocked_default_builder,
    )

    panel = TodaysTop3Panel(model)

    assert panel.view_model is model
    assert panel.state_badge.text() == 'Ready'


def test_todays_top3_panel_contract_has_no_runtime_side_effect_paths():
    source = TODAYS_TOP3_PANEL.read_text(encoding='utf-8')

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


def test_mission_control_wires_todays_top3_only_from_prepared_view_model():
    source = MAIN_WINDOW.read_text(encoding='utf-8')

    assert 'TodaysTop3Panel(self._todays_top3_view_model)' in source
    assert 'build_todays_top3_view_model' not in source
    assert 'TodaysTop3ViewModel | None = None' in source


def test_mission_control_places_todays_top3_after_next_steps_before_dashboard_grid():
    _application()
    health_model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS'),
    )
    operational_model = _ready_operational_model()
    next_steps_model = _ready_next_steps_model()
    todays_top3_model = _ready_todays_top3_model()
    mission = _MissionControlService()
    window = MainWindow(
        mission,
        _InventoryService(),
        health_model,
        operational_model,
        next_steps_model,
        todays_top3_view_model=todays_top3_model,
    )

    layout = window.inventory_panel.layout()
    assert layout.itemAt(0).widget() is window.mission_control_header
    assert layout.itemAt(1).widget() is window.header_status_band
    assert layout.itemAt(2).widget() is window.health_status_card
    assert layout.itemAt(3).widget() is window.operational_status_strip
    assert layout.itemAt(4).widget() is window.next_steps_panel
    assert layout.itemAt(5).widget() is window.todays_top3_panel
    assert layout.itemAt(6).widget() is window.dashboard_grid_shell
    assert window.todays_top3_panel.view_model is todays_top3_model

    first_panel = window.todays_top3_panel
    window.refresh()
    assert window.todays_top3_panel is first_panel
    assert mission.snapshot_calls == 2
