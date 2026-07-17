from dataclasses import FrozenInstanceError

import pytest

from app.engines.mission_control.opportunity_risk import (
    OPPORTUNITY_RISK_KIND_ORDER,
    OpportunityRiskGroup,
    OpportunityRiskItem,
    OpportunityRiskViewModel,
    build_opportunity_risk_view_model,
    opportunity_risk_evidence,
)


def _item(
    kind: str,
    display_order: int,
    candidate_key: str,
    *,
    state: str = 'ready',
    label: str | None = None,
    top3_relationship: str = 'independent',
    independent_evidence_summary: str | None = None,
) -> OpportunityRiskItem:
    return opportunity_risk_evidence(
        kind,
        state=state,
        display_order=display_order,
        candidate_key=candidate_key,
        label=label or f'{kind} {display_order}',
        why_it_matters=f'{kind} {display_order} may change if Mark waits.',
        direction_label=f'{kind} condition',
        evidence_summary=f'{kind} {display_order} prepared local evidence.',
        source_authority='Prepared local evidence',
        freshness_label='As of prepared local snapshot',
        top3_relationship=top3_relationship,
        independent_evidence_summary=independent_evidence_summary,
    )


def test_build_opportunity_risk_view_model_preserves_group_and_item_order():
    model = build_opportunity_risk_view_model(
        evidence=(
            _item('risk', 2, 'risk-b'),
            _item('opportunity', 2, 'opportunity-b'),
            _item('risk', 1, 'risk-a'),
            _item('opportunity', 1, 'opportunity-a'),
        )
    )

    assert model == OpportunityRiskViewModel(
        state='ready',
        headline='Opportunity + Risk ready',
        groups=(
            OpportunityRiskGroup(
                kind='opportunity',
                state='ready',
                title='Opportunities',
                evidence_summary='Opportunities prepared local evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Prepared local freshness',
                items=(
                    _item('opportunity', 1, 'opportunity-a'),
                    _item('opportunity', 2, 'opportunity-b'),
                ),
            ),
            OpportunityRiskGroup(
                kind='risk',
                state='ready',
                title='Risks',
                evidence_summary='Risks prepared local evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Prepared local freshness',
                items=(
                    _item('risk', 1, 'risk-a'),
                    _item('risk', 2, 'risk-b'),
                ),
            ),
        ),
    )
    assert tuple(group.kind for group in model.groups) == OPPORTUNITY_RISK_KIND_ORDER


def test_missing_evidence_is_unavailable_without_fake_opportunity_or_risk_values():
    model = build_opportunity_risk_view_model()

    assert model.state == 'unavailable'
    assert model.headline == 'Opportunity + Risk unavailable'
    assert tuple(group.kind for group in model.groups) == OPPORTUNITY_RISK_KIND_ORDER
    assert [group.title for group in model.groups] == ['Opportunities', 'Risks']
    assert all(group.state == 'unavailable' for group in model.groups)
    assert all(group.items == () for group in model.groups)
    assert model.groups[0].evidence_summary == 'Prepared local Opportunity evidence unavailable.'
    assert model.groups[1].evidence_summary == 'Prepared local Risk evidence unavailable.'


def test_partial_state_when_one_group_or_item_is_incomplete():
    model = build_opportunity_risk_view_model(
        evidence=(
            _item('opportunity', 1, 'opportunity-a'),
            _item('risk', 1, 'risk-a', state='partial'),
        )
    )

    assert model.state == 'partial'
    assert model.headline == 'Opportunity + Risk partially available'
    assert model.groups[0].state == 'ready'
    assert model.groups[1].state == 'partial'


def test_partial_state_when_only_one_group_has_evidence():
    model = build_opportunity_risk_view_model(
        evidence=(
            _item('opportunity', 1, 'opportunity-a'),
        )
    )

    assert model.state == 'partial'
    assert model.groups[0].state == 'ready'
    assert model.groups[1].state == 'unavailable'


def test_error_safe_state_preserves_injected_groups_inline():
    model = build_opportunity_risk_view_model(
        evidence=(
            _item('opportunity', 1, 'opportunity-a'),
            _item('risk', 1, 'risk-a'),
        ),
        error_text='Prepared Opportunity + Risk evidence could not be read.',
    )

    assert model.state == 'error'
    assert model.headline == 'Opportunity + Risk unavailable'
    assert model.error_text == 'Prepared Opportunity + Risk evidence could not be read.'
    assert tuple(group.kind for group in model.groups) == OPPORTUNITY_RISK_KIND_ORDER
    assert model.groups[0].items[0].candidate_key == 'opportunity-a'
    assert model.groups[1].items[0].candidate_key == 'risk-a'


def test_exact_todays_top3_candidate_keys_are_excluded_by_contract():
    model = build_opportunity_risk_view_model(
        evidence=(
            _item('opportunity', 1, 'same-as-top3'),
            _item('opportunity', 2, 'broader-opportunity'),
            _item('risk', 1, 'risk-a'),
        ),
        excluded_todays_top3_candidate_keys=('same-as-top3',),
    )

    assert model.excluded_todays_top3_candidate_keys == ('same-as-top3',)
    assert [item.candidate_key for item in model.groups[0].items] == [
        'broader-opportunity',
    ]
    assert model.groups[1].items[0].candidate_key == 'risk-a'


def test_broader_related_top3_conditions_require_independent_evidence():
    model = build_opportunity_risk_view_model(
        evidence=(
            _item(
                'opportunity',
                1,
                'broader-opportunity',
                top3_relationship='broader_related',
                independent_evidence_summary='Separate local listing-readiness evidence supports visibility.',
            ),
            _item('risk', 1, 'risk-a'),
        )
    )

    opportunity = model.groups[0].items[0]
    assert opportunity.top3_relationship == 'broader_related'
    assert (
        opportunity.independent_evidence_summary
        == 'Separate local listing-readiness evidence supports visibility.'
    )


def test_opportunity_risk_contract_is_immutable():
    model = build_opportunity_risk_view_model(
        evidence=(
            _item('opportunity', 1, 'opportunity-a'),
            _item('risk', 1, 'risk-a'),
        )
    )

    with pytest.raises(FrozenInstanceError):
        model.headline = 'Changed'

    with pytest.raises(FrozenInstanceError):
        model.groups[0].title = 'Changed'

    with pytest.raises(FrozenInstanceError):
        model.groups[0].items[0].label = 'Changed'


@pytest.mark.parametrize(
    ('builder', 'exception'),
    [
        (lambda: build_opportunity_risk_view_model(evidence=[]), TypeError),
        (
            lambda: build_opportunity_risk_view_model(
                evidence=(
                    _item('opportunity', 1, 'same-key'),
                    _item('risk', 1, 'same-key'),
                )
            ),
            ValueError,
        ),
        (
            lambda: build_opportunity_risk_view_model(
                evidence=(
                    _item('opportunity', 1, 'opportunity-a'),
                    _item('opportunity', 2, 'opportunity-b'),
                    _item('opportunity', 3, 'opportunity-c'),
                    _item('opportunity', 4, 'opportunity-d'),
                )
            ),
            ValueError,
        ),
        (
            lambda: build_opportunity_risk_view_model(
                excluded_todays_top3_candidate_keys=['top3']
            ),
            TypeError,
        ),
        (
            lambda: build_opportunity_risk_view_model(
                excluded_todays_top3_candidate_keys=('top3', 'top3')
            ),
            ValueError,
        ),
        (lambda: build_opportunity_risk_view_model(error_text=' '), ValueError),
        (
            lambda: opportunity_risk_evidence(
                'watchlist',
                state='ready',
                display_order=1,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Today',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='live',
                display_order=1,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Today',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=0,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Today',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=1,
                candidate_key=' ',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Today',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=1,
                candidate_key='candidate-a',
                label=' ',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Today',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=1,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters=' ',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Today',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=1,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label=' ',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Today',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=1,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary=' ',
                source_authority='Prepared local evidence',
                freshness_label='Today',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=1,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority=' ',
                freshness_label='Today',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=1,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label=' ',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=1,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Today',
                top3_relationship='exact',
            ),
            ValueError,
        ),
        (
            lambda: opportunity_risk_evidence(
                'opportunity',
                state='ready',
                display_order=1,
                candidate_key='candidate-a',
                label='Candidate',
                why_it_matters='Prepared reason.',
                direction_label='Opening',
                evidence_summary='Prepared evidence.',
                source_authority='Prepared local evidence',
                freshness_label='Today',
                top3_relationship='broader_related',
            ),
            ValueError,
        ),
    ],
)
def test_opportunity_risk_rejects_invalid_inputs(builder, exception):
    with pytest.raises(exception):
        builder()


def test_contract_types_are_publicly_constructible():
    item = OpportunityRiskItem(
        kind='opportunity',
        state='unavailable',
        display_order=1,
        candidate_key='opportunity-a',
        label='Opportunity unavailable',
        why_it_matters='Evidence unavailable.',
        direction_label='Unavailable',
        evidence_summary='Evidence unavailable.',
        source_authority='Local evidence unavailable',
        freshness_label='Freshness unavailable',
    )
    group = OpportunityRiskGroup(
        kind='opportunity',
        state='unavailable',
        title='Opportunities',
        evidence_summary='Evidence unavailable.',
        source_authority='Local evidence unavailable',
        freshness_label='Freshness unavailable',
        items=(item,),
    )

    model = OpportunityRiskViewModel(
        state='partial',
        headline='Opportunity + Risk partially available',
        groups=(
            group,
            OpportunityRiskGroup(
                kind='risk',
                state='unavailable',
                title='Risks',
                evidence_summary='Evidence unavailable.',
                source_authority='Local evidence unavailable',
                freshness_label='Freshness unavailable',
                items=(),
            ),
        ),
    )

    assert model.groups[0].items[0] == item
