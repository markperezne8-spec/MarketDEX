from app.engines.health.status_view_model import build_health_status_view_model
from PySide6.QtWidgets import QApplication, QPushButton
from ui.health_status_card import HealthStatusCard
from ui.main_window import MainWindow


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


def test_health_status_card_renders_injected_available_view_model():
    _application()
    model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS'),
    )
    card = HealthStatusCard(model)
    assert card.title_label.text() == 'System Health'
    assert card.state_badge.text() == 'Ready'
    assert card.status_label.text() == 'Health ready'
    assert card.diagnostics_label.text() == 'runtime=MarketDEX\noverall=PASS'
    assert card.view_model is model


def test_health_status_card_renders_deterministic_empty_diagnostics():
    _application()
    model = build_health_status_view_model(status_text=None)
    card = HealthStatusCard(model)
    assert card.status_label.text() == 'Health status unavailable'
    assert card.state_badge.text() == 'Unavailable'
    assert card.diagnostics_label.text() == 'No diagnostic details available.'


def test_health_status_card_renders_error_safely_without_dialogs():
    _application()
    model = build_health_status_view_model(
        status_text=None,
        diagnostic_lines=('registration=desktop-health', 'runtime=MarketDEX'),
        error_text='Health evidence unavailable',
    )
    card = HealthStatusCard(model)

    assert card.state_badge.text() == 'Error-safe'
    assert card.status_label.text() == 'Health status unavailable'
    assert card.error_label.text() == 'Health evidence unavailable'
    assert not card.error_label.isHidden()
    assert card.diagnostics_label.text() == 'registration=desktop-health\nruntime=MarketDEX'


def test_health_status_card_has_no_action_controls():
    _application()
    model = build_health_status_view_model(status_text='Health ready')
    card = HealthStatusCard(model)

    assert card.findChildren(QPushButton) == []
    assert card.header_actions.count() == 0
    assert card.view_model is model


def test_mission_control_places_health_card_below_header_and_above_kpis():
    _application()
    model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS'),
    )
    mission = _MissionControlService()
    window = MainWindow(mission, _InventoryService(), model)

    layout = window.inventory_panel.layout()
    assert layout.itemAt(0).widget() is window.mission_control_header
    assert layout.itemAt(1).widget() is window.health_status_card
    assert layout.itemAt(2).layout() is not None
    assert window.health_status_card.view_model is model
    assert window.health_status_card.state_badge.text() == 'Ready'

    first_card = window.health_status_card
    window.refresh()
    assert window.health_status_card is first_card
    assert mission.snapshot_calls == 2
