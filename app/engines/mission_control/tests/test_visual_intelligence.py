import pytest

from app.engines.mission_control.visual_intelligence import (
    VISUAL_INTELLIGENCE_REGION_ORDER,
    build_visual_intelligence_view_model,
    visual_intelligence_evidence,
)


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


def test_missing_evidence_is_unavailable_in_stable_region_order():
    view_model = build_visual_intelligence_view_model()

    assert view_model.state == 'unavailable'
    assert tuple(region.region for region in view_model.regions) == (
        *VISUAL_INTELLIGENCE_REGION_ORDER,
    )
    assert all(region.state == 'unavailable' for region in view_model.regions)


def test_injected_evidence_is_reordered_and_complete_evidence_is_ready():
    evidence = tuple(
        _evidence(region)
        for region in reversed(VISUAL_INTELLIGENCE_REGION_ORDER)
    )

    view_model = build_visual_intelligence_view_model(evidence=evidence)

    assert view_model.state == 'ready'
    assert tuple(region.region for region in view_model.regions) == (
        *VISUAL_INTELLIGENCE_REGION_ORDER,
    )


def test_missing_region_keeps_surface_partial_without_inventing_evidence():
    evidence = tuple(
        _evidence(region)
        for region in VISUAL_INTELLIGENCE_REGION_ORDER[:2]
    )

    view_model = build_visual_intelligence_view_model(evidence=evidence)

    assert view_model.state == 'partial'
    assert view_model.regions[2].state == 'unavailable'
    assert view_model.regions[2].source_authority == 'Local evidence unavailable'


def test_partial_injected_region_produces_partial_view_model():
    evidence = tuple(
        _evidence(
            region,
            state='partial' if region == 'inventory_alerts' else 'ready',
        )
        for region in VISUAL_INTELLIGENCE_REGION_ORDER
    )

    view_model = build_visual_intelligence_view_model(evidence=evidence)

    assert view_model.state == 'partial'
    assert view_model.regions[1].state == 'partial'


def test_error_text_produces_error_safe_view_model():
    view_model = build_visual_intelligence_view_model(
        error_text='Prepared evidence adapter failed.'
    )

    assert view_model.state == 'error'
    assert view_model.error_text == 'Prepared evidence adapter failed.'
    assert all(region.state == 'unavailable' for region in view_model.regions)


def test_outputs_are_immutable():
    view_model = build_visual_intelligence_view_model()

    with pytest.raises((AttributeError, TypeError)):
        view_model.state = 'ready'


def test_duplicate_regions_are_rejected():
    with pytest.raises(ValueError, match='at most once'):
        build_visual_intelligence_view_model(
            evidence=(_evidence('inventory_alerts'), _evidence('inventory_alerts'))
        )


@pytest.mark.parametrize(
    'builder, expected_exception',
    [
        (lambda: _evidence('unknown'), ValueError),
        (lambda: build_visual_intelligence_view_model(evidence=[]), TypeError),
        (
            lambda: visual_intelligence_evidence(
                'performance_charts',
                state='ready',
                subtitle='',
                evidence_summary='evidence',
                source_authority='source',
                freshness_label='freshness',
                detail='detail',
            ),
            ValueError,
        ),
    ],
)
def test_invalid_inputs_are_rejected_deterministically(builder, expected_exception):
    with pytest.raises(expected_exception):
        builder()
