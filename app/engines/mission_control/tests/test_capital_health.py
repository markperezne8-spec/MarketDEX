from dataclasses import FrozenInstanceError

import pytest

from app.engines.mission_control.capital_health import (
    CAPITAL_HEALTH_GROUP_ORDER,
    CapitalHealthGroupEvidence,
    CapitalHealthMetric,
    CapitalHealthViewModel,
    build_capital_health_view_model,
    capital_health_group_evidence,
    capital_health_metric,
)


def _metric(label: str, value_label: str = 'Prepared local value', state: str = 'ready'):
    return capital_health_metric(
        label,
        state=state,
        value_label=value_label,
        evidence_summary=f'{label} prepared local evidence.',
    )


def _group(group: str, state: str = 'ready') -> CapitalHealthGroupEvidence:
    return capital_health_group_evidence(
        group,
        state=state,
        evidence_summary=f'{group} prepared local evidence.',
        source_authority='Prepared local evidence',
        period_label='90 days',
        explanation=f'{group} remains read-only.',
        metrics=(
            _metric(f'{group} metric', state=state),
        ),
    )


def test_build_capital_health_view_model_preserves_group_order():
    model = build_capital_health_view_model(
        evidence=(
            _group('growth'),
            _group('availability'),
            _group('commitment'),
            _group('recycling'),
        )
    )

    assert model == CapitalHealthViewModel(
        state='ready',
        headline='Capital Health ready',
        groups=(
            _group('availability'),
            _group('recycling'),
            _group('commitment'),
            _group('growth'),
        ),
    )
    assert tuple(group.group for group in model.groups) == CAPITAL_HEALTH_GROUP_ORDER


def test_missing_evidence_is_unavailable_without_inventing_capital_values():
    model = build_capital_health_view_model()

    assert model.state == 'unavailable'
    assert model.headline == 'Capital Health unavailable'
    assert tuple(group.group for group in model.groups) == CAPITAL_HEALTH_GROUP_ORDER
    assert all(group.state == 'unavailable' for group in model.groups)
    assert [group.title for group in model.groups] == [
        'Availability',
        'Recycling',
        'Commitment',
        'Growth',
    ]

    availability = model.groups[0]
    assert [metric.label for metric in availability.metrics] == [
        'Available Cash',
        'Available for Redeployment',
    ]
    assert all(metric.value_label == 'Unavailable' for metric in availability.metrics)

    recycling = model.groups[1]
    assert recycling.metrics[0].label == 'Capital Recycling Rate'
    assert recycling.metrics[0].value_label == 'Unavailable'

    growth = model.groups[3]
    assert growth.metrics[0].label == 'Business-cycle Capital Growth'
    assert growth.metrics[0].value_label == 'Unavailable'
    assert 'external cash injection' in growth.explanation


def test_available_cash_and_redeployment_are_distinct_metrics():
    availability = capital_health_group_evidence(
        'availability',
        state='ready',
        evidence_summary='Prepared local availability evidence.',
        source_authority='Prepared local evidence',
        period_label='Today',
        explanation='Availability keeps cash and redeployment separate.',
        metrics=(
            _metric('Available Cash', '$10 prepared value'),
            _metric('Available for Redeployment', '$4 prepared value'),
        ),
    )

    model = build_capital_health_view_model(evidence=(availability,))

    assert model.state == 'partial'
    assert [metric.label for metric in model.groups[0].metrics] == [
        'Available Cash',
        'Available for Redeployment',
    ]
    assert [metric.value_label for metric in model.groups[0].metrics] == [
        '$10 prepared value',
        '$4 prepared value',
    ]


def test_partial_and_missing_evidence_produce_partial_state():
    model = build_capital_health_view_model(
        evidence=(
            _group('availability'),
            _group('recycling', 'partial'),
        )
    )

    assert model.state == 'partial'
    assert model.headline == 'Capital Health partially available'
    assert model.groups[0].state == 'ready'
    assert model.groups[1].state == 'partial'
    assert model.groups[2].state == 'unavailable'
    assert model.groups[3].state == 'unavailable'


def test_error_safe_state_preserves_injected_groups_inline():
    model = build_capital_health_view_model(
        evidence=(
            _group('availability'),
        ),
        error_text='Prepared Capital Health evidence could not be read.',
    )

    assert model.state == 'error'
    assert model.headline == 'Capital Health unavailable'
    assert model.error_text == 'Prepared Capital Health evidence could not be read.'
    assert tuple(group.group for group in model.groups) == CAPITAL_HEALTH_GROUP_ORDER
    assert model.groups[0].state == 'ready'
    assert model.groups[1].state == 'unavailable'
    assert model.groups[2].state == 'unavailable'
    assert model.groups[3].state == 'unavailable'


def test_capital_health_contract_is_immutable():
    model = build_capital_health_view_model(
        evidence=(
            _group('availability'),
        )
    )

    with pytest.raises(FrozenInstanceError):
        model.headline = 'Changed'

    with pytest.raises(FrozenInstanceError):
        model.groups[0].title = 'Changed'

    with pytest.raises(FrozenInstanceError):
        model.groups[0].metrics[0].value_label = 'Changed'


@pytest.mark.parametrize(
    ('builder', 'exception'),
    [
        (lambda: build_capital_health_view_model(evidence=[]), TypeError),
        (
            lambda: build_capital_health_view_model(
                evidence=(
                    _group('availability'),
                    _group('availability'),
                )
            ),
            ValueError,
        ),
        (lambda: build_capital_health_view_model(error_text=' '), ValueError),
        (
            lambda: capital_health_group_evidence(
                'score',
                state='ready',
                evidence_summary='Evidence.',
                source_authority='Local.',
                period_label='90 days.',
                explanation='Explanation.',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: capital_health_group_evidence(
                'availability',
                state='live',
                evidence_summary='Evidence.',
                source_authority='Local.',
                period_label='90 days.',
                explanation='Explanation.',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: capital_health_group_evidence(
                'availability',
                state='ready',
                evidence_summary=' ',
                source_authority='Local.',
                period_label='90 days.',
                explanation='Explanation.',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: capital_health_group_evidence(
                'availability',
                state='ready',
                evidence_summary='Evidence.',
                source_authority=' ',
                period_label='90 days.',
                explanation='Explanation.',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: capital_health_group_evidence(
                'availability',
                state='ready',
                evidence_summary='Evidence.',
                source_authority='Local.',
                period_label=' ',
                explanation='Explanation.',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: capital_health_group_evidence(
                'availability',
                state='ready',
                evidence_summary='Evidence.',
                source_authority='Local.',
                period_label='90 days.',
                explanation=' ',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: capital_health_group_evidence(
                'availability',
                state='ready',
                evidence_summary='Evidence.',
                source_authority='Local.',
                period_label='90 days.',
                explanation='Explanation.',
                metrics=(),
            ),
            TypeError,
        ),
        (
            lambda: capital_health_metric(
                ' ',
                state='ready',
                value_label='Value.',
                evidence_summary='Evidence.',
            ),
            ValueError,
        ),
        (
            lambda: capital_health_metric(
                'Metric',
                state='live',
                value_label='Value.',
                evidence_summary='Evidence.',
            ),
            ValueError,
        ),
        (
            lambda: capital_health_metric(
                'Metric',
                state='ready',
                value_label=' ',
                evidence_summary='Evidence.',
            ),
            ValueError,
        ),
        (
            lambda: capital_health_metric(
                'Metric',
                state='ready',
                value_label='Value.',
                evidence_summary=' ',
            ),
            ValueError,
        ),
    ],
)
def test_capital_health_rejects_invalid_inputs(builder, exception):
    with pytest.raises(exception):
        builder()


def test_contract_types_are_publicly_constructible():
    metric = CapitalHealthMetric(
        label='Available Cash',
        state='unavailable',
        value_label='Unavailable',
        evidence_summary='Evidence unavailable.',
    )
    group = CapitalHealthGroupEvidence(
        group='availability',
        state='unavailable',
        title='Availability',
        evidence_summary='Evidence unavailable.',
        source_authority='Local evidence unavailable',
        period_label='Period unavailable',
        explanation='No prepared local evidence.',
        metrics=(metric,),
    )

    assert build_capital_health_view_model(evidence=(group,)).groups[0] == group
