from dataclasses import FrozenInstanceError

import pytest

from app.engines.mission_control.todays_top3 import (
    TODAYS_TOP3_RANK_ORDER,
    TodaysTop3Evidence,
    TodaysTop3ViewModel,
    build_todays_top3_view_model,
    todays_top3_evidence,
)


def _evidence(rank: int, title: str, state: str = 'ready'):
    return todays_top3_evidence(
        rank,
        state=state,
        title=title,
        reason=f'{title} has prepared local evidence.',
        evidence_summary=f'{title} evidence summary.',
        affected_area='Inventory',
        next_safe_preparation=f'Prepare local review for {title}.',
    )


def test_build_todays_top3_view_model_preserves_rank_order():
    model = build_todays_top3_view_model(
        evidence=(
            _evidence(3, 'Review audit coverage'),
            _evidence(1, 'Review listing readiness'),
            _evidence(2, 'Review inventory age'),
        )
    )

    assert model == TodaysTop3ViewModel(
        state='ready',
        headline='Today\'s Top 3 ready',
        items=(
            TodaysTop3Evidence(
                rank=1,
                state='ready',
                title='Review listing readiness',
                reason='Review listing readiness has prepared local evidence.',
                evidence_summary='Review listing readiness evidence summary.',
                affected_area='Inventory',
                next_safe_preparation=(
                    'Prepare local review for Review listing readiness.'
                ),
            ),
            TodaysTop3Evidence(
                rank=2,
                state='ready',
                title='Review inventory age',
                reason='Review inventory age has prepared local evidence.',
                evidence_summary='Review inventory age evidence summary.',
                affected_area='Inventory',
                next_safe_preparation='Prepare local review for Review inventory age.',
            ),
            TodaysTop3Evidence(
                rank=3,
                state='ready',
                title='Review audit coverage',
                reason='Review audit coverage has prepared local evidence.',
                evidence_summary='Review audit coverage evidence summary.',
                affected_area='Inventory',
                next_safe_preparation='Prepare local review for Review audit coverage.',
            ),
        ),
    )
    assert tuple(item.rank for item in model.items) == TODAYS_TOP3_RANK_ORDER


def test_missing_evidence_is_unavailable_without_inventing_priorities():
    model = build_todays_top3_view_model()

    assert model.state == 'unavailable'
    assert model.headline == 'Today\'s Top 3 unavailable'
    assert tuple(item.rank for item in model.items) == TODAYS_TOP3_RANK_ORDER
    assert all(item.state == 'unavailable' for item in model.items)
    assert [item.title for item in model.items] == [
        'Priority 1 unavailable',
        'Priority 2 unavailable',
        'Priority 3 unavailable',
    ]
    assert all(item.reason == 'Evidence unavailable.' for item in model.items)
    assert all(item.evidence_summary == 'Evidence unavailable.' for item in model.items)
    assert all(item.affected_area == 'Unassigned' for item in model.items)
    assert all(
        item.next_safe_preparation == 'No safe local preparation available.'
        for item in model.items
    )


def test_partial_and_missing_evidence_produce_partial_state():
    model = build_todays_top3_view_model(
        evidence=(
            _evidence(1, 'Review listing readiness'),
            _evidence(2, 'Review inventory age', 'partial'),
        )
    )

    assert model.state == 'partial'
    assert model.headline == 'Today\'s Top 3 partially available'
    assert model.items[0].state == 'ready'
    assert model.items[1].state == 'partial'
    assert model.items[2].state == 'unavailable'


def test_error_safe_state_preserves_injected_items_inline():
    model = build_todays_top3_view_model(
        evidence=(
            _evidence(1, 'Review listing readiness'),
        ),
        error_text='Prepared Today\'s Top 3 evidence could not be read.',
    )

    assert model.state == 'error'
    assert model.headline == 'Today\'s Top 3 unavailable'
    assert model.error_text == 'Prepared Today\'s Top 3 evidence could not be read.'
    assert tuple(item.rank for item in model.items) == TODAYS_TOP3_RANK_ORDER
    assert model.items[0].title == 'Review listing readiness'
    assert model.items[1].state == 'unavailable'
    assert model.items[2].state == 'unavailable'


def test_todays_top3_contract_is_immutable():
    model = build_todays_top3_view_model(
        evidence=(
            _evidence(1, 'Review listing readiness'),
        )
    )

    with pytest.raises(FrozenInstanceError):
        model.headline = 'Changed'

    with pytest.raises(FrozenInstanceError):
        model.items[0].title = 'Changed'


@pytest.mark.parametrize(
    ('builder', 'exception'),
    [
        (lambda: build_todays_top3_view_model(evidence=[]), TypeError),
        (
            lambda: build_todays_top3_view_model(
                evidence=(
                    _evidence(1, 'one'),
                    _evidence(1, 'two'),
                )
            ),
            ValueError,
        ),
        (lambda: build_todays_top3_view_model(error_text=' '), ValueError),
        (
            lambda: todays_top3_evidence(
                4,
                state='ready',
                title='Unsupported rank',
                reason='Reason.',
                evidence_summary='Evidence.',
                affected_area='Inventory',
                next_safe_preparation='Prepare.',
            ),
            ValueError,
        ),
        (
            lambda: todays_top3_evidence(
                1,
                state='live',
                title='Unsupported state',
                reason='Reason.',
                evidence_summary='Evidence.',
                affected_area='Inventory',
                next_safe_preparation='Prepare.',
            ),
            ValueError,
        ),
        (
            lambda: todays_top3_evidence(
                1,
                state='ready',
                title=' ',
                reason='Reason.',
                evidence_summary='Evidence.',
                affected_area='Inventory',
                next_safe_preparation='Prepare.',
            ),
            ValueError,
        ),
        (
            lambda: todays_top3_evidence(
                1,
                state='ready',
                title='Title',
                reason=' ',
                evidence_summary='Evidence.',
                affected_area='Inventory',
                next_safe_preparation='Prepare.',
            ),
            ValueError,
        ),
        (
            lambda: todays_top3_evidence(
                1,
                state='ready',
                title='Title',
                reason='Reason.',
                evidence_summary=' ',
                affected_area='Inventory',
                next_safe_preparation='Prepare.',
            ),
            ValueError,
        ),
        (
            lambda: todays_top3_evidence(
                1,
                state='ready',
                title='Title',
                reason='Reason.',
                evidence_summary='Evidence.',
                affected_area=' ',
                next_safe_preparation='Prepare.',
            ),
            ValueError,
        ),
        (
            lambda: todays_top3_evidence(
                1,
                state='ready',
                title='Title',
                reason='Reason.',
                evidence_summary='Evidence.',
                affected_area='Inventory',
                next_safe_preparation=' ',
            ),
            ValueError,
        ),
    ],
)
def test_todays_top3_rejects_invalid_inputs(builder, exception):
    with pytest.raises(exception):
        builder()
