from dataclasses import FrozenInstanceError

import pytest

from app.engines.mission_control.business_scoreboard import (
    BUSINESS_SCOREBOARD_GROUP_ORDER,
    BusinessScoreboardGroupEvidence,
    BusinessScoreboardMetric,
    BusinessScoreboardViewModel,
    build_business_scoreboard_view_model,
    business_scoreboard_group_evidence,
    business_scoreboard_metric,
)


def _metric(label: str, value_label: str | None = None, state: str = 'ready'):
    if value_label is None:
        value_label = 'Not applicable' if state == 'not_applicable' else 'Prepared local value'
    return business_scoreboard_metric(
        label,
        state=state,
        value_label=value_label,
        period_label='90 DAYS',
        evidence_summary=f'{label} prepared local evidence.',
        source_authority='Prepared local evidence',
        calculation_authority=f'{label} prepared calculation authority.',
    )


def _group(group: str, state: str = 'ready') -> BusinessScoreboardGroupEvidence:
    return business_scoreboard_group_evidence(
        group,
        state=state,
        evidence_summary=f'{group} prepared local evidence.',
        source_authority='Prepared local evidence',
        period_label='90 DAYS',
        metrics=(
            _metric(f'{group} metric', state=state),
        ),
    )


def test_build_business_scoreboard_view_model_preserves_group_order():
    model = build_business_scoreboard_view_model(
        evidence=(
            _group('throughput'),
            _group('money'),
        )
    )

    assert model == BusinessScoreboardViewModel(
        state='ready',
        headline='Business Scoreboard ready',
        selected_period_label='90 DAYS',
        groups=(
            _group('money'),
            _group('throughput'),
        ),
    )
    assert tuple(group.group for group in model.groups) == BUSINESS_SCOREBOARD_GROUP_ORDER


def test_missing_evidence_is_unavailable_without_fake_scoreboard_values():
    model = build_business_scoreboard_view_model()

    assert model.state == 'unavailable'
    assert model.headline == 'Business Scoreboard unavailable'
    assert model.selected_period_label == '90 DAYS'
    assert tuple(group.group for group in model.groups) == BUSINESS_SCOREBOARD_GROUP_ORDER
    assert all(group.state == 'unavailable' for group in model.groups)
    assert [group.title for group in model.groups] == ['Money', 'Throughput']

    money = model.groups[0]
    assert [metric.label for metric in money.metrics] == [
        'Seller Net Proceeds',
        'Net Business Gain',
        'Capital Recycled This Period',
    ]
    assert all(metric.value_label == 'Unavailable' for metric in money.metrics)
    assert all(metric.period_label == '90 DAYS' for metric in money.metrics)

    throughput = model.groups[1]
    assert [metric.label for metric in throughput.metrics] == [
        'Orders Completed',
        'Items Sold',
        'Median Days to Sell',
    ]
    assert all(metric.value_label == 'Unavailable' for metric in throughput.metrics)


def test_injected_period_labels_are_preserved_without_calculation():
    money = business_scoreboard_group_evidence(
        'money',
        state='ready',
        evidence_summary='Prepared local money evidence.',
        source_authority='Prepared local order settlement evidence',
        period_label='30 DAYS',
        metrics=(
            business_scoreboard_metric(
                'Seller Net Proceeds',
                state='ready',
                value_label='Prepared local value',
                period_label='30 DAYS',
                evidence_summary='Prepared settlement evidence.',
                source_authority='Prepared local settlement evidence',
                calculation_authority='Prepared local calculation authority',
            ),
        ),
    )

    model = build_business_scoreboard_view_model(
        evidence=(money,),
        selected_period_label='30 DAYS',
    )

    assert model.state == 'partial'
    assert model.selected_period_label == '30 DAYS'
    assert model.groups[0] == money
    assert model.groups[0].metrics[0].period_label == '30 DAYS'
    assert model.groups[0].metrics[0].value_label == 'Prepared local value'
    assert model.groups[1].state == 'unavailable'
    assert all(metric.period_label == '30 DAYS' for metric in model.groups[1].metrics)


def test_partial_state_when_one_group_or_metric_is_incomplete():
    model = build_business_scoreboard_view_model(
        evidence=(
            _group('money'),
            _group('throughput', 'partial'),
        )
    )

    assert model.state == 'partial'
    assert model.headline == 'Business Scoreboard partially available'
    assert model.groups[0].state == 'ready'
    assert model.groups[1].state == 'partial'


def test_not_applicable_state_is_preserved_for_inapplicable_periods():
    model = build_business_scoreboard_view_model(
        evidence=(
            _group('money', 'not_applicable'),
            _group('throughput', 'not_applicable'),
        )
    )

    assert model.state == 'not_applicable'
    assert model.headline == 'Business Scoreboard not applicable'
    assert all(group.state == 'not_applicable' for group in model.groups)
    assert all(
        metric.state == 'not_applicable'
        for group in model.groups
        for metric in group.metrics
    )


def test_error_safe_state_preserves_injected_groups_inline():
    model = build_business_scoreboard_view_model(
        evidence=(
            _group('money'),
        ),
        error_text='Prepared Business Scoreboard evidence could not be read.',
    )

    assert model.state == 'error'
    assert model.headline == 'Business Scoreboard unavailable'
    assert model.error_text == 'Prepared Business Scoreboard evidence could not be read.'
    assert tuple(group.group for group in model.groups) == BUSINESS_SCOREBOARD_GROUP_ORDER
    assert model.groups[0].state == 'ready'
    assert model.groups[1].state == 'unavailable'


@pytest.mark.parametrize(
    (
        'model',
        'expected_state',
        'expected_headline',
        'expected_error_text',
        'expected_group_states',
    ),
    [
        (
            build_business_scoreboard_view_model(
                evidence=(
                    _group('money'),
                    _group('throughput'),
                )
            ),
            'ready',
            'Business Scoreboard ready',
            None,
            ('ready', 'ready'),
        ),
        (
            build_business_scoreboard_view_model(),
            'unavailable',
            'Business Scoreboard unavailable',
            None,
            ('unavailable', 'unavailable'),
        ),
        (
            build_business_scoreboard_view_model(
                evidence=(
                    _group('money'),
                )
            ),
            'partial',
            'Business Scoreboard partially available',
            None,
            ('ready', 'unavailable'),
        ),
        (
            build_business_scoreboard_view_model(
                evidence=(
                    _group('money', 'not_applicable'),
                    _group('throughput', 'not_applicable'),
                )
            ),
            'not_applicable',
            'Business Scoreboard not applicable',
            None,
            ('not_applicable', 'not_applicable'),
        ),
        (
            build_business_scoreboard_view_model(
                evidence=(
                    _group('money'),
                ),
                error_text='Prepared Business Scoreboard evidence could not be read.',
            ),
            'error',
            'Business Scoreboard unavailable',
            'Prepared Business Scoreboard evidence could not be read.',
            ('ready', 'unavailable'),
        ),
    ],
)
def test_business_scoreboard_display_state_matrix_is_locked(
    model,
    expected_state,
    expected_headline,
    expected_error_text,
    expected_group_states,
):
    assert model.state == expected_state
    assert model.headline == expected_headline
    assert model.error_text == expected_error_text
    assert tuple(group.group for group in model.groups) == BUSINESS_SCOREBOARD_GROUP_ORDER
    assert tuple(group.state for group in model.groups) == expected_group_states


def test_business_scoreboard_metric_state_order_is_locked():
    metric_states = ('ready', 'partial', 'unavailable', 'not_applicable', 'error')
    money = business_scoreboard_group_evidence(
        'money',
        state='partial',
        evidence_summary='money prepared local evidence.',
        source_authority='Prepared local evidence',
        period_label='90 DAYS',
        metrics=tuple(
            _metric(f'money metric {state}', state=state)
            for state in metric_states
        ),
    )

    model = build_business_scoreboard_view_model(
        evidence=(
            money,
            _group('throughput'),
        )
    )

    assert model.state == 'partial'
    assert tuple(metric.state for metric in model.groups[0].metrics) == metric_states
    assert [metric.label for metric in model.groups[0].metrics] == [
        'money metric ready',
        'money metric partial',
        'money metric unavailable',
        'money metric not_applicable',
        'money metric error',
    ]
    assert all(metric.period_label == '90 DAYS' for metric in model.groups[0].metrics)
    assert all(
        metric.source_authority == 'Prepared local evidence'
        for metric in model.groups[0].metrics
    )
    assert all(
        metric.calculation_authority.endswith('prepared calculation authority.')
        for metric in model.groups[0].metrics
    )


def test_business_scoreboard_contract_is_immutable():
    model = build_business_scoreboard_view_model(
        evidence=(
            _group('money'),
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
        (lambda: build_business_scoreboard_view_model(evidence=[]), TypeError),
        (
            lambda: build_business_scoreboard_view_model(
                evidence=(
                    _group('money'),
                    _group('money'),
                )
            ),
            ValueError,
        ),
        (
            lambda: build_business_scoreboard_view_model(selected_period_label=' '),
            ValueError,
        ),
        (lambda: build_business_scoreboard_view_model(error_text=' '), ValueError),
        (
            lambda: business_scoreboard_group_evidence(
                'capital_health',
                state='ready',
                evidence_summary='Evidence.',
                source_authority='Local.',
                period_label='90 DAYS',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_group_evidence(
                'money',
                state='live',
                evidence_summary='Evidence.',
                source_authority='Local.',
                period_label='90 DAYS',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_group_evidence(
                'money',
                state='ready',
                evidence_summary=' ',
                source_authority='Local.',
                period_label='90 DAYS',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_group_evidence(
                'money',
                state='ready',
                evidence_summary='Evidence.',
                source_authority=' ',
                period_label='90 DAYS',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_group_evidence(
                'money',
                state='ready',
                evidence_summary='Evidence.',
                source_authority='Local.',
                period_label=' ',
                metrics=(_metric('Metric'),),
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_group_evidence(
                'money',
                state='ready',
                evidence_summary='Evidence.',
                source_authority='Local.',
                period_label='90 DAYS',
                metrics=(),
            ),
            TypeError,
        ),
        (
            lambda: business_scoreboard_metric(
                ' ',
                state='ready',
                value_label='Value.',
                period_label='90 DAYS',
                evidence_summary='Evidence.',
                source_authority='Local.',
                calculation_authority='Calculation.',
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_metric(
                'Metric',
                state='live',
                value_label='Value.',
                period_label='90 DAYS',
                evidence_summary='Evidence.',
                source_authority='Local.',
                calculation_authority='Calculation.',
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_metric(
                'Metric',
                state='ready',
                value_label=' ',
                period_label='90 DAYS',
                evidence_summary='Evidence.',
                source_authority='Local.',
                calculation_authority='Calculation.',
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_metric(
                'Metric',
                state='ready',
                value_label='Value.',
                period_label=' ',
                evidence_summary='Evidence.',
                source_authority='Local.',
                calculation_authority='Calculation.',
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_metric(
                'Metric',
                state='ready',
                value_label='Value.',
                period_label='90 DAYS',
                evidence_summary=' ',
                source_authority='Local.',
                calculation_authority='Calculation.',
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_metric(
                'Metric',
                state='ready',
                value_label='Value.',
                period_label='90 DAYS',
                evidence_summary='Evidence.',
                source_authority=' ',
                calculation_authority='Calculation.',
            ),
            ValueError,
        ),
        (
            lambda: business_scoreboard_metric(
                'Metric',
                state='ready',
                value_label='Value.',
                period_label='90 DAYS',
                evidence_summary='Evidence.',
                source_authority='Local.',
                calculation_authority=' ',
            ),
            ValueError,
        ),
    ],
)
def test_business_scoreboard_rejects_invalid_inputs(builder, exception):
    with pytest.raises(exception):
        builder()


def test_contract_types_are_publicly_constructible():
    metric = BusinessScoreboardMetric(
        label='Seller Net Proceeds',
        state='unavailable',
        value_label='Unavailable',
        period_label='90 DAYS',
        evidence_summary='Evidence unavailable.',
        source_authority='Local evidence unavailable',
        calculation_authority='Calculation authority unavailable',
    )
    group = BusinessScoreboardGroupEvidence(
        group='money',
        state='unavailable',
        title='Money',
        evidence_summary='Prepared local Money outcome evidence unavailable.',
        source_authority='Local evidence unavailable',
        period_label='90 DAYS',
        metrics=(metric,),
    )

    assert build_business_scoreboard_view_model(evidence=(group,)).groups[0] == group
