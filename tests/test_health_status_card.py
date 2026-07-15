from app.engines.health.status_view_model import build_health_status_view_model
from PySide6.QtWidgets import QApplication
from ui.health_status_card import HealthStatusCard


def _application():
    return QApplication.instance() or QApplication([])


def test_health_status_card_renders_injected_available_view_model():
    _application()
    model = build_health_status_view_model(
        status_text='Health ready',
        diagnostic_lines=('runtime=MarketDEX', 'overall=PASS'),
    )
    card = HealthStatusCard(model)
    assert card.title_label.text() == 'System Health'
    assert card.status_label.text() == 'Health ready'
    assert card.diagnostics_label.text() == 'runtime=MarketDEX\noverall=PASS'
    assert card.view_model is model


def test_health_status_card_renders_deterministic_empty_diagnostics():
    _application()
    model = build_health_status_view_model(status_text=None)
    card = HealthStatusCard(model)
    assert card.status_label.text() == 'Health status unavailable'
    assert card.diagnostics_label.text() == 'No diagnostic details available.'
