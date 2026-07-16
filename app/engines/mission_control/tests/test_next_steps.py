from dataclasses import FrozenInstanceError

import pytest

from app.engines.mission_control.next_steps import (
    NEXT_STEP_READINESS_GROUP_ORDER,
    NextStepReadinessEvidence,
    NextStepReadinessViewModel,
    build_next_step_readiness_view_model,
    next_step_readiness_evidence,
)


def _evidence(group: str, detail: str, state: str = 'ready'):
    return next_step_readiness_evidence(group, state=state, detail=detail)


def test_build_next_step_readiness_view_model_preserves_group_order():
    model = build_next_step_readiness_view_model(
        evidence=(
            _evidence('readiness_note', 'Prepare the local inventory review.'),
            _evidence('authority_audit_readiness', 'Audit evidence is present.'),
            _evidence('inventory_readiness', 'Inventory evidence is present.'),
            _evidence('next_safe_action', 'Review prepared inventory data.'),
        )
    )

    assert model == NextStepReadinessViewModel(
        state='ready',
        headline='Action readiness ready',
        groups=(
            NextStepReadinessEvidence(
                group='next_safe_action',
                state='ready',
                label='Next safe action',
                detail='Review prepared inventory data.',
            ),
            NextStepReadinessEvidence(
                group='inventory_readiness',
                state='ready',
                label='Inventory readiness',
                detail='Inventory evidence is present.',
            ),
            NextStepReadinessEvidence(
                group='authority_audit_readiness',
                state='ready',
                label='Authority/audit readiness',
                detail='Audit evidence is present.',
            ),
            NextStepReadinessEvidence(
                group='readiness_note',
                state='ready',
                label='Readiness note',
                detail='Prepare the local inventory review.',
            ),
        ),
    )
    assert tuple(group.group for group in model.groups) == (
        NEXT_STEP_READINESS_GROUP_ORDER
    )


def test_missing_evidence_is_unavailable_without_inventing_status():
    model = build_next_step_readiness_view_model()

    assert model.state == 'unavailable'
    assert model.headline == 'Action readiness unavailable'
    assert tuple(group.group for group in model.groups) == (
        NEXT_STEP_READINESS_GROUP_ORDER
    )
    assert all(group.state == 'unavailable' for group in model.groups)
    assert all(group.detail == 'Evidence unavailable.' for group in model.groups)


def test_missing_and_partial_evidence_produce_partial_state():
    model = build_next_step_readiness_view_model(
        evidence=(
            _evidence('next_safe_action', 'Review prepared inventory data.'),
            _evidence(
                'inventory_readiness',
                'Some inventory evidence is missing.',
                'partial',
            ),
        )
    )

    assert model.state == 'partial'
    assert model.headline == 'Action readiness partially available'
    assert model.groups[1].state == 'partial'
    assert model.groups[2].state == 'unavailable'
    assert model.groups[3].state == 'unavailable'


def test_error_safe_state_preserves_injected_groups_inline():
    model = build_next_step_readiness_view_model(
        evidence=(
            _evidence('next_safe_action', 'Prepared action could not be rendered.'),
        ),
        error_text='Prepared readiness evidence could not be read.',
    )

    assert model.state == 'error'
    assert model.headline == 'Action readiness unavailable'
    assert model.error_text == 'Prepared readiness evidence could not be read.'
    assert tuple(group.group for group in model.groups) == (
        NEXT_STEP_READINESS_GROUP_ORDER
    )


def test_next_step_readiness_contract_is_immutable():
    model = build_next_step_readiness_view_model(
        evidence=(
            _evidence('next_safe_action', 'Review prepared inventory data.'),
        )
    )

    with pytest.raises(FrozenInstanceError):
        model.headline = 'Changed'

    with pytest.raises(FrozenInstanceError):
        model.groups[0].detail = 'Changed'


@pytest.mark.parametrize(
    ('builder', 'exception'),
    [
        (lambda: build_next_step_readiness_view_model(evidence=[]), TypeError),
        (
            lambda: build_next_step_readiness_view_model(
                evidence=(
                    _evidence('next_safe_action', 'one'),
                    _evidence('next_safe_action', 'two'),
                )
            ),
            ValueError,
        ),
        (lambda: build_next_step_readiness_view_model(error_text=' '), ValueError),
        (
            lambda: next_step_readiness_evidence(
                'unknown', state='ready', detail='unsupported'
            ),
            ValueError,
        ),
        (
            lambda: next_step_readiness_evidence(
                'next_safe_action', state='live', detail='unsupported'
            ),
            ValueError,
        ),
        (
            lambda: next_step_readiness_evidence(
                'inventory_readiness', state='ready', detail=' '
            ),
            ValueError,
        ),
        (
            lambda: next_step_readiness_evidence(
                'readiness_note', state='ready', detail='Ready.', label=' '
            ),
            ValueError,
        ),
    ],
)
def test_next_step_readiness_rejects_invalid_inputs(builder, exception):
    with pytest.raises(exception):
        builder()
