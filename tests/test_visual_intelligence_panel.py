import pytest
from PySide6.QtWidgets import QApplication, QPushButton

from app.engines.mission_control.visual_intelligence import (
    VISUAL_INTELLIGENCE_REGION_ORDER,
    build_visual_intelligence_view_model,
    visual_intelligence_evidence,
)
from ui.design_system.widgets import StatusTone
from ui.visual_intelligence_panel import (
    VISUAL_INTELLIGENCE_REGION_VISUAL_CONTRACT,
    VISUAL_INTELLIGENCE_VISUAL_CONTRACT,
    VisualIntelligencePanel,
    visual_intelligence_state_badge_contract,
)


def _application():
    return QApplication.instance() or QApplication([])


def _evidence(region, *, state='ready'):
    return visual_intelligence_evidence(
        region,
        state=state,
        subtitle='Prepared local evidence',
        evidence_summary='Prepared evidence supplied.',
        source_authority='Prepared local evidence',
        freshness_label='Prepared local freshness',
        detail='Read-only evidence detail.',
    )


def test_panel_renders_default_unavailable_contract_in_stable_order():
    _application()
    panel = VisualIntelligencePanel()

    assert panel.title_label.text() == 'Visual Intelligence'
    assert panel.description_label.text() == (
        'Read-only visual intelligence and alert-region shell'
    )
    assert panel.property('dashboardRole') == 'visual-intelligence-shell'
    assert panel.property('visualContract') == VISUAL_INTELLIGENCE_VISUAL_CONTRACT
    assert panel.property('visualIntelligenceState') == 'unavailable'
    assert panel.property('visualIntelligenceRegionOrder') == ','.join(
        VISUAL_INTELLIGENCE_REGION_ORDER
    )
    assert panel.state_badge.text() == 'Unavailable'
    assert panel.state_badge.property('tone') == StatusTone.WARNING.value
    assert panel.headline_label.text() == 'Visual Intelligence unavailable'
    assert [widget.property('visualIntelligenceRegion') for widget in panel.region_widgets] == [
        *VISUAL_INTELLIGENCE_REGION_ORDER,
    ]
    assert [badge.text() for badge in panel.findChildren(type(panel.state_badge))] == [
        'Unavailable',
        'Unavailable',
        'Unavailable',
        'Unavailable',
        'Unavailable',
    ]


def test_panel_renders_injected_model_without_fallback_builder(monkeypatch):
    _application()
    model = build_visual_intelligence_view_model(
        evidence=tuple(
            _evidence(region)
            for region in VISUAL_INTELLIGENCE_REGION_ORDER
        )
    )

    def _blocked_default_builder():
        raise AssertionError('injected view model should not use the fallback builder')

    monkeypatch.setattr(
        'ui.visual_intelligence_panel.build_visual_intelligence_view_model',
        _blocked_default_builder,
    )

    panel = VisualIntelligencePanel(model)

    assert panel.view_model is model
    assert panel.state_badge.text() == 'Ready'
    assert panel.headline_label.text() == 'Visual Intelligence ready'
    assert [widget.property('visualIntelligenceState') for widget in panel.region_widgets] == [
        'ready',
        'ready',
        'ready',
        'ready',
    ]


def test_panel_preserves_partial_and_error_safe_display_states():
    _application()
    partial_model = build_visual_intelligence_view_model(
        evidence=(
            _evidence('performance_charts', state='partial'),
        )
    )
    error_model = build_visual_intelligence_view_model(
        error_text='Prepared visual evidence could not be read.'
    )

    partial_panel = VisualIntelligencePanel(partial_model)
    error_panel = VisualIntelligencePanel(error_model)

    assert partial_panel.state_badge.text() == 'Partial'
    assert partial_panel.region_widgets[0].findChildren(type(partial_panel.state_badge))[0].text() == 'Partial'
    assert error_panel.state_badge.text() == 'Error-safe'
    assert error_panel.error_label.text() == (
        'Prepared visual evidence could not be read.'
    )
    assert not error_panel.error_label.isHidden()


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
    assert visual_intelligence_state_badge_contract(state) == (label, tone)


def test_panel_has_no_action_controls_or_runtime_side_effects():
    _application()
    panel = VisualIntelligencePanel()

    assert panel.findChildren(QPushButton) == []
    assert panel.view_model.state == 'unavailable'
    assert all(
        region.source_authority == 'Local evidence unavailable'
        for region in panel.view_model.regions
    )
    assert all(
        widget.property('visualContract')
        == VISUAL_INTELLIGENCE_REGION_VISUAL_CONTRACT
        for widget in panel.region_widgets
    )
