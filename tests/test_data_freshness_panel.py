import pytest
from PySide6.QtWidgets import QApplication, QPushButton

from app.engines.mission_control.data_freshness import (
    DATA_FRESHNESS_DOMAIN_ORDER,
    build_data_freshness_view_model,
    data_freshness_evidence,
)
from ui.data_freshness_panel import (
    DATA_FRESHNESS_DOMAIN_VISUAL_CONTRACT,
    DATA_FRESHNESS_VISUAL_CONTRACT,
    DataFreshnessPanel,
    data_freshness_state_badge_contract,
)
from ui.design_system.widgets import StatusTone


def _application():
    return QApplication.instance() or QApplication([])


def _evidence(domain, *, state='ready'):
    return data_freshness_evidence(
        domain,
        state=state,
        source_authority='Prepared local evidence',
        as_of_label='As of prepared evidence',
        freshness_label='Prepared freshness',
        detail='Read-only evidence detail.',
    )


def test_panel_renders_default_unavailable_contract_in_stable_order():
    _application()
    panel = DataFreshnessPanel()

    assert panel.title_label.text() == 'Data Freshness'
    assert panel.property('dashboardRole') == 'data-freshness-shell'
    assert panel.property('visualContract') == DATA_FRESHNESS_VISUAL_CONTRACT
    assert panel.property('dataFreshnessState') == 'unavailable'
    assert panel.property('dataFreshnessDomainOrder') == ','.join(
        DATA_FRESHNESS_DOMAIN_ORDER
    )
    assert panel.state_badge.text() == 'Unavailable'
    assert panel.headline_label.text() == 'Data Freshness unavailable'
    assert [widget.property('dataFreshnessDomain') for widget in panel.domain_widgets] == [
        *DATA_FRESHNESS_DOMAIN_ORDER,
    ]
    assert all(
        domain.detail == 'Evidence unavailable.'
        for domain in panel.view_model.domains
    )


def test_panel_renders_injected_ready_model():
    _application()
    model = build_data_freshness_view_model(
        evidence=tuple(_evidence(domain) for domain in DATA_FRESHNESS_DOMAIN_ORDER)
    )

    panel = DataFreshnessPanel(model)

    assert panel.view_model is model
    assert panel.state_badge.text() == 'Ready'
    assert panel.headline_label.text() == 'Data Freshness ready'
    assert [widget.property('dataFreshnessState') for widget in panel.domain_widgets] == [
        'ready',
        'ready',
        'ready',
        'ready',
    ]


def test_panel_preserves_partial_and_error_safe_states():
    _application()
    partial = DataFreshnessPanel(
        build_data_freshness_view_model(evidence=(_evidence('inventory'),))
    )
    error = DataFreshnessPanel(
        build_data_freshness_view_model(error_text='Prepared evidence could not be read.')
    )

    assert partial.state_badge.text() == 'Partial'
    assert error.state_badge.text() == 'Error-safe'
    assert error.error_label.text() == 'Prepared evidence could not be read.'
    assert not error.error_label.isHidden()


@pytest.mark.parametrize(
    ('state', 'label', 'tone'),
    [
        ('ready', 'Ready', StatusTone.POSITIVE),
        ('unavailable', 'Unavailable', StatusTone.WARNING),
        ('partial', 'Partial', StatusTone.WARNING),
        ('error', 'Error-safe', StatusTone.NEGATIVE),
    ],
)
def test_state_badge_contract_is_locked(state, label, tone):
    assert data_freshness_state_badge_contract(state) == (label, tone)


def test_panel_has_no_action_controls_or_side_effects():
    _application()
    panel = DataFreshnessPanel()

    assert panel.findChildren(QPushButton) == []
    assert all(
        widget.property('visualContract') == DATA_FRESHNESS_DOMAIN_VISUAL_CONTRACT
        for widget in panel.domain_widgets
    )
