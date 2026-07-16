from pathlib import Path

from PySide6.QtWidgets import QApplication, QPushButton

from app.engines.health.status_view_model import build_health_status_view_model
from app.engines.mission_control.header_status import (
    build_header_status_view_model,
    header_status_evidence,
)
from app.engines.mission_control.next_steps import (
    build_next_step_readiness_view_model,
    next_step_readiness_evidence,
)
from app.engines.mission_control.operational_status import (
    build_operational_status_view_model,
    operational_status_evidence,
)
from ui.design_system.tokens import NorthStarPanelTone
from ui.design_system.widgets import StatusTone
from ui.header_status_band import HeaderStatusBand
from ui.main_window import MainWindow

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEADER_STATUS_BAND = REPOSITORY_ROOT / 'ui' / 'header_status_band.py'
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


def _ready_header_status_model():
    return build_header_status_view_model(
        evidence=(
            header_status_evidence(
                'operating_context',
                state='ready',
                detail='Mission Control context is prepared.',
            ),
            header_status_evidence(
                'app_status',
                state='ready',
                detail='Offline-first app shell is prepared.',
            ),
            header_status_evidence(
                'data_freshness',
                state='ready',
                detail='Prepared freshness evidence is available.',
            ),
            header_status_evidence(
                'workbook_health',
                state='ready',
                detail='Prepared workbook evidence is available.',
            ),
            header_status_evidence(
                'local_authority',
                state='ready',
                detail='Local authority evidence is prepared.',
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


def test_header_status_band_renders_injected_view_model_in_order():
    _application()
    model = _ready_header_status_model()
    band = HeaderStatusBand(model)

    assert band.title_label.text() == 'Command Status'
    assert band.description_label.text() == 'Read-only North Star header readiness'
    assert band.property('northStarTone') == NorthStarPanelTone.COMMAND.value
    assert band.state_badge.text() == 'Ready'
    assert band.state_badge.property('tone') == StatusTone.POSITIVE.value
    assert band.headline_label.text() == 'Header status ready'
    assert band.view_model is model
    assert [badge.text() for badge in band.slot_state_badges] == [
        'Ready',
        'Ready',
        'Ready',
        'Ready',
        'Ready',
    ]
    assert [label.text() for label in band.slot_labels] == [
        'Operating context',
        'Mission Control context is prepared.',
        'App/offline status',
        'Offline-first app shell is prepared.',
        'Data freshness',
        'Prepared freshness evidence is available.',
        'Workbook health',
        'Prepared workbook evidence is available.',
        'Local authority',
        'Local authority evidence is prepared.',
    ]


def test_header_status_band_renders_default_unavailable_state():
    _application()
    band = HeaderStatusBand()

    assert band.state_badge.text() == 'Unavailable'
    assert band.state_badge.property('tone') == StatusTone.WARNING.value
    assert band.headline_label.text() == 'Header status unavailable'
    assert [badge.text() for badge in band.slot_state_badges] == [
        'Unavailable',
        'Unavailable',
        'Unavailable',
        'Unavailable',
        'Unavailable',
    ]
    assert [label.text() for label in band.slot_labels] == [
        'Operating context',
        'Evidence unavailable.',
        'App/offline status',
        'Evidence unavailable.',
        'Data freshness',
        'Evidence unavailable.',
        'Workbook health',
        'Evidence unavailable.',
        'Local authority',
        'Evidence unavailable.',
    ]


def test_header_status_band_renders_partial_state_without_inventing_evidence():
    _application()
    model = build_header_status_view_model(
        evidence=(
            header_status_evidence(
                'operating_context',
                state='ready',
                detail='Mission Control context is prepared.',
            ),
            header_status_evidence(
                'data_freshness',
                state='partial',
                detail='Freshness contract is not approved yet.',
            ),
        )
    )
    band = HeaderStatusBand(model)

    assert band.state_badge.text() == 'Partial'
    assert band.state_badge.property('tone') == StatusTone.WARNING.value
    assert band.headline_label.text() == 'Header status partially available'
    assert [badge.text() for badge in band.slot_state_badges] == [
        'Ready',
        'Unavailable',
        'Partial',
        'Unavailable',
        'Unavailable',
    ]


def test_header_status_band_renders_error_safely_inline():
    _application()
    model = build_header_status_view_model(
        evidence=(
            header_status_evidence(
                'operating_context',
                state='ready',
                detail='Mission Control context is prepared.',
            ),
        ),
        error_text='Prepared header status evidence could not be read.',
    )
    band = HeaderStatusBand(model)

    assert band.state_badge.text() == 'Error-safe'
    assert band.state_badge.property('tone') == StatusTone.NEGATIVE.value
    assert band.headline_label.text() == 'Header status unavailable'
    assert band.error_label.text() == (
        'Prepared header status evidence could not be read.'
    )
    assert not band.error_label.isHidden()
    assert [badge.text() for badge in band.slot_state_badges] == [
        'Ready',
        'Unavailable',
        'Unavailable',
        'Unavailable',
        'Unavailable',
    ]


def test_header_status_band_has_no_action_controls():
    _application()
    band = HeaderStatusBand(_ready_header_status_model())

    assert band.findChildren(QPushButton) == []
    assert band.header_actions.count() == 0


def test_header_status_band_uses_injected_model_without_fallback_builder(monkeypatch):
    _application()
    model = _ready_header_status_model()

    def _blocked_default_builder():
        raise AssertionError('injected view model should not use the fallback builder')

    monkeypatch.setattr(
        'ui.header_status_band.build_header_status_view_model',
        _blocked_default_builder,
    )

    band = HeaderStatusBand(model)

    assert band.view_model is model
    assert band.state_badge.text() == 'Ready'


def test_header_status_band_contract_has_no_runtime_side_effect_paths():
    source = HEADER_STATUS_BAND.read_text(encoding='utf-8')

    prohibited_tokens = (
        'QMessageBox',
        'QDialog',
        'QTimer',
        'socket',
        'requests',
        'urllib',
        'sqlite3',
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


def test_mission_control_wires_header_status_only_from_prepared_view_model():
    source = MAIN_WINDOW.read_text(encoding='utf-8')

    assert 'HeaderStatusBand(self._header_status_view_model)' in source
    assert 'build_header_status_view_model' not in source
    assert 'HeaderStatusViewModel | None = None' in source


def test_mission_control_places_header_status_band_between_header_and_health():
    _application()
    health_model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS'),
    )
    header_status_model = _ready_header_status_model()
    operational_model = _ready_operational_model()
    next_steps_model = _ready_next_steps_model()
    mission = _MissionControlService()
    window = MainWindow(
        mission,
        _InventoryService(),
        health_model,
        operational_model,
        next_steps_model,
        header_status_model,
    )

    layout = window.inventory_panel.layout()
    assert layout.itemAt(0).widget() is window.mission_control_header
    assert layout.itemAt(1).widget() is window.header_status_band
    assert layout.itemAt(2).widget() is window.health_status_card
    assert layout.itemAt(3).widget() is window.operational_status_strip
    assert layout.itemAt(4).widget() is window.next_steps_panel
    assert layout.itemAt(5).layout() is not None
    assert window.header_status_band.view_model is header_status_model
    assert window.health_status_card.view_model is health_model
    assert window.operational_status_strip.view_model is operational_model
    assert window.next_steps_panel.view_model is next_steps_model

    first_band = window.header_status_band
    window.refresh()
    assert window.header_status_band is first_band
    assert mission.snapshot_calls == 2
