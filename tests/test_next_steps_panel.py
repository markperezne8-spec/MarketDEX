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
from ui.design_system.widgets import StatusTone
from ui.main_window import MainWindow
from ui.next_steps_panel import NextStepsPanel

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
NEXT_STEPS_PANEL = REPOSITORY_ROOT / 'ui' / 'next_steps_panel.py'
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


def test_next_steps_panel_renders_injected_view_model_in_order():
    _application()
    model = _ready_next_steps_model()
    panel = NextStepsPanel(model)

    assert panel.title_label.text() == 'Next Steps'
    assert panel.state_badge.text() == 'Ready'
    assert panel.state_badge.property('tone') == StatusTone.POSITIVE.value
    assert panel.headline_label.text() == 'Action readiness ready'
    assert panel.view_model is model
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Ready',
        'Ready',
        'Ready',
        'Ready',
    ]
    assert [
        badge.property('tone') for badge in panel.group_state_badges
    ] == [StatusTone.POSITIVE.value] * 4
    assert [label.text() for label in panel.group_labels] == [
        'Next safe action',
        'Prepare the next local inventory review.',
        'Inventory readiness',
        'Inventory summary is prepared locally.',
        'Authority/audit readiness',
        'Authority evidence is prepared locally.',
        'Readiness note',
        'No action has been started.',
    ]


def test_next_steps_panel_renders_default_unavailable_state():
    _application()
    panel = NextStepsPanel()

    assert panel.state_badge.text() == 'Unavailable'
    assert panel.state_badge.property('tone') == StatusTone.WARNING.value
    assert panel.headline_label.text() == 'Action readiness unavailable'
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Unavailable',
        'Unavailable',
        'Unavailable',
        'Unavailable',
    ]
    assert [
        badge.property('tone') for badge in panel.group_state_badges
    ] == [StatusTone.WARNING.value] * 4
    assert [label.text() for label in panel.group_labels] == [
        'Next safe action',
        'Evidence unavailable.',
        'Inventory readiness',
        'Evidence unavailable.',
        'Authority/audit readiness',
        'Evidence unavailable.',
        'Readiness note',
        'Evidence unavailable.',
    ]


def test_next_steps_panel_renders_partial_state_without_inventing_evidence():
    _application()
    model = build_next_step_readiness_view_model(
        evidence=(
            next_step_readiness_evidence(
                'next_safe_action',
                state='ready',
                detail='Prepare local inventory review.',
            ),
            next_step_readiness_evidence(
                'inventory_readiness',
                state='partial',
                detail='Inventory summary is present; audit detail is unavailable.',
            ),
        )
    )
    panel = NextStepsPanel(model)

    assert panel.state_badge.text() == 'Partial'
    assert panel.state_badge.property('tone') == StatusTone.WARNING.value
    assert panel.headline_label.text() == 'Action readiness partially available'
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Ready',
        'Partial',
        'Unavailable',
        'Unavailable',
    ]
    assert [label.text() for label in panel.group_labels] == [
        'Next safe action',
        'Prepare local inventory review.',
        'Inventory readiness',
        'Inventory summary is present; audit detail is unavailable.',
        'Authority/audit readiness',
        'Evidence unavailable.',
        'Readiness note',
        'Evidence unavailable.',
    ]


def test_next_steps_panel_renders_error_safely_inline():
    _application()
    model = build_next_step_readiness_view_model(
        evidence=(
            next_step_readiness_evidence(
                'next_safe_action',
                state='ready',
                detail='Prepare local inventory review.',
            ),
        ),
        error_text='Prepared action readiness evidence could not be read.',
    )
    panel = NextStepsPanel(model)

    assert panel.state_badge.text() == 'Error-safe'
    assert panel.state_badge.property('tone') == StatusTone.NEGATIVE.value
    assert panel.headline_label.text() == 'Action readiness unavailable'
    assert panel.error_label.text() == (
        'Prepared action readiness evidence could not be read.'
    )
    assert not panel.error_label.isHidden()
    assert [badge.text() for badge in panel.group_state_badges] == [
        'Ready',
        'Unavailable',
        'Unavailable',
        'Unavailable',
    ]


def test_next_steps_panel_has_no_action_controls():
    _application()
    panel = NextStepsPanel(_ready_next_steps_model())

    assert panel.findChildren(QPushButton) == []
    assert panel.header_actions.count() == 0


def test_next_steps_panel_uses_injected_model_without_fallback_builder(monkeypatch):
    _application()
    model = _ready_next_steps_model()

    def _blocked_default_builder():
        raise AssertionError('injected view model should not use the fallback builder')

    monkeypatch.setattr(
        'ui.next_steps_panel.build_next_step_readiness_view_model',
        _blocked_default_builder,
    )

    panel = NextStepsPanel(model)

    assert panel.view_model is model
    assert panel.state_badge.text() == 'Ready'


def test_next_steps_panel_contract_has_no_runtime_side_effect_paths():
    source = NEXT_STEPS_PANEL.read_text(encoding='utf-8')

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


def test_mission_control_wires_next_steps_only_from_prepared_view_model():
    source = MAIN_WINDOW.read_text(encoding='utf-8')

    assert 'NextStepsPanel(self._next_steps_view_model)' in source
    assert 'build_next_step_readiness_view_model' not in source
    assert 'NextStepReadinessViewModel | None = None' in source


def test_mission_control_places_next_steps_after_operational_strip_and_above_kpis():
    _application()
    health_model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS'),
    )
    operational_model = _ready_operational_model()
    next_steps_model = _ready_next_steps_model()
    mission = _MissionControlService()
    window = MainWindow(
        mission,
        _InventoryService(),
        health_model,
        operational_model,
        next_steps_model,
    )

    layout = window.inventory_panel.layout()
    assert layout.itemAt(0).widget() is window.mission_control_header
    assert layout.itemAt(1).widget() is window.header_status_band
    assert layout.itemAt(2).widget() is window.health_status_card
    assert layout.itemAt(3).widget() is window.operational_status_strip
    assert layout.itemAt(4).widget() is window.next_steps_panel
    assert layout.itemAt(5).widget() is window.dashboard_grid_shell
    assert window.dashboard_grid_shell.property('visualContract') == (
        'm1.14e-north-star-dashboard-grid-shell'
    )
    assert window.health_status_card.view_model is health_model
    assert window.operational_status_strip.view_model is operational_model
    assert window.next_steps_panel.view_model is next_steps_model

    first_panel = window.next_steps_panel
    window.refresh()
    assert window.next_steps_panel is first_panel
    assert mission.snapshot_calls == 2


def test_mission_control_dashboard_grid_shell_preserves_existing_kpis_and_placeholders():
    _application()
    window = MainWindow(
        _MissionControlService(),
        _InventoryService(),
        next_steps_view_model=_ready_next_steps_model(),
    )

    assert window.dashboard_grid_visual_contract == (
        'm1.14e-north-star-dashboard-grid-shell'
    )
    assert window.dashboard_grid_shell.property('dashboardRole') == 'dashboard-grid-shell'
    assert window.dashboard_grid_shell.header_actions.count() == 1
    assert window.dashboard_grid_shell.header_actions.itemAt(0).widget().text() == 'Read-only'
    assert set(window.values) == {
        'inventory_units',
        'inventory_asset_count',
        'inventory_cost_minor',
        'completed_sales',
        'revenue_minor',
        'profit_minor',
        'verified_audits',
        'authority_events',
    }

    placeholders = [
        panel for panel in window.dashboard_grid_shell.findChildren(QWidget)
        if panel.property('dashboardRole') == 'future-contract-placeholder'
    ]
    assert len(placeholders) == 4
    assert [panel.title_label.text() for panel in placeholders] == [
        'Inventory Command Center',
        'Capital Health',
        'Opportunity + Risk',
        'Visual Intelligence',
    ]
    assert all(
        'Evidence unavailable. Future contract required.'
        in panel.accessibleName()
        for panel in placeholders
    )
