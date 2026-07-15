from PySide6.QtWidgets import QApplication, QPushButton

from app.engines.health.status_view_model import build_health_status_view_model
from app.engines.mission_control.operational_status import (
    build_operational_status_view_model,
    operational_status_evidence,
)
from ui.main_window import MainWindow
from ui.operational_status_strip import OperationalStatusStrip


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


def test_operational_status_strip_renders_injected_view_model_in_order():
    _application()
    model = _ready_operational_model()
    strip = OperationalStatusStrip(model)

    assert strip.title_label.text() == 'Operational Status'
    assert strip.state_badge.text() == 'Ready'
    assert strip.headline_label.text() == 'Operational status ready'
    assert strip.view_model is model
    assert [label.text() for label in strip.group_labels] == [
        'Local authority',
        'Local runtime authority is present.',
        'Offline-first',
        'No network evidence is required.',
        'Inventory readiness',
        'Inventory snapshot is locally available.',
        'Audit/authority evidence',
        'Verified audit evidence is present.',
    ]


def test_operational_status_strip_renders_default_unavailable_state():
    _application()
    strip = OperationalStatusStrip()

    assert strip.state_badge.text() == 'Unavailable'
    assert strip.headline_label.text() == 'Operational status unavailable'
    assert [label.text() for label in strip.group_labels] == [
        'Local authority',
        'Evidence unavailable.',
        'Offline-first',
        'Evidence unavailable.',
        'Inventory readiness',
        'Evidence unavailable.',
        'Audit/authority evidence',
        'Evidence unavailable.',
    ]


def test_operational_status_strip_has_no_action_controls():
    _application()
    strip = OperationalStatusStrip(_ready_operational_model())

    assert strip.findChildren(QPushButton) == []
    assert strip.header_actions.count() == 0


def test_mission_control_places_operational_strip_after_health_card_and_above_kpis():
    _application()
    health_model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS'),
    )
    operational_model = _ready_operational_model()
    mission = _MissionControlService()
    window = MainWindow(
        mission,
        _InventoryService(),
        health_model,
        operational_model,
    )

    layout = window.inventory_panel.layout()
    assert layout.itemAt(0).widget() is window.mission_control_header
    assert layout.itemAt(1).widget() is window.health_status_card
    assert layout.itemAt(2).widget() is window.operational_status_strip
    assert layout.itemAt(3).layout() is not None
    assert window.health_status_card.view_model is health_model
    assert window.operational_status_strip.view_model is operational_model

    first_strip = window.operational_status_strip
    window.refresh()
    assert window.operational_status_strip is first_strip
    assert mission.snapshot_calls == 2
