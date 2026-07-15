from dataclasses import FrozenInstanceError

import pytest

from app.engines.mission_control.operational_status import (
    OPERATIONAL_STATUS_GROUP_ORDER,
    OperationalStatusEvidence,
    OperationalStatusViewModel,
    build_operational_status_view_model,
    operational_status_evidence,
)


def _evidence(group: str, detail: str, state: str = 'available'):
    return operational_status_evidence(group, state=state, detail=detail)


def test_build_operational_status_view_model_preserves_deterministic_group_order():
    model = build_operational_status_view_model(
        evidence=(
            _evidence('inventory', 'Inventory snapshot is locally available.'),
            _evidence('audit_authority', 'Verified audit evidence is present.'),
            _evidence('local_authority', 'Local runtime authority is present.'),
            _evidence('offline_first', 'No network evidence is required.'),
        )
    )

    assert model == OperationalStatusViewModel(
        state='available',
        headline='Operational status ready',
        groups=(
            OperationalStatusEvidence(
                group='local_authority',
                state='available',
                label='Local authority',
                detail='Local runtime authority is present.',
            ),
            OperationalStatusEvidence(
                group='offline_first',
                state='available',
                label='Offline-first',
                detail='No network evidence is required.',
            ),
            OperationalStatusEvidence(
                group='inventory',
                state='available',
                label='Inventory readiness',
                detail='Inventory snapshot is locally available.',
            ),
            OperationalStatusEvidence(
                group='audit_authority',
                state='available',
                label='Audit/authority evidence',
                detail='Verified audit evidence is present.',
            ),
        ),
    )
    assert tuple(group.group for group in model.groups) == OPERATIONAL_STATUS_GROUP_ORDER


def test_build_operational_status_view_model_marks_missing_groups_unavailable():
    model = build_operational_status_view_model(
        evidence=(
            _evidence('local_authority', 'Local runtime authority is present.'),
            _evidence('offline_first', 'No network evidence is required.'),
        )
    )

    assert model.state == 'partial'
    assert model.headline == 'Operational status partially available'
    assert tuple(group.group for group in model.groups) == OPERATIONAL_STATUS_GROUP_ORDER
    assert model.groups[2] == OperationalStatusEvidence(
        group='inventory',
        state='unavailable',
        label='Inventory readiness',
        detail='Evidence unavailable.',
    )
    assert model.groups[3] == OperationalStatusEvidence(
        group='audit_authority',
        state='unavailable',
        label='Audit/authority evidence',
        detail='Evidence unavailable.',
    )


def test_build_operational_status_view_model_has_deterministic_unavailable_state():
    model = build_operational_status_view_model()

    assert model.state == 'unavailable'
    assert model.headline == 'Operational status unavailable'
    assert all(group.state == 'unavailable' for group in model.groups)
    assert tuple(group.group for group in model.groups) == OPERATIONAL_STATUS_GROUP_ORDER


def test_build_operational_status_view_model_preserves_partial_evidence_state():
    model = build_operational_status_view_model(
        evidence=(
            _evidence('local_authority', 'Local runtime authority is present.'),
            _evidence('offline_first', 'No network evidence is required.'),
            _evidence('inventory', 'Inventory readiness needs review.', 'partial'),
            _evidence('audit_authority', 'Verified audit evidence is present.'),
        )
    )

    assert model.state == 'partial'
    assert model.groups[2].state == 'partial'
    assert model.groups[2].detail == 'Inventory readiness needs review.'


def test_build_operational_status_view_model_has_error_safe_state():
    model = build_operational_status_view_model(
        evidence=(
            _evidence('local_authority', 'Local runtime authority is present.'),
        ),
        error_text='Prepared operational evidence could not be read.',
    )

    assert model.state == 'error'
    assert model.headline == 'Operational status unavailable'
    assert model.error_text == 'Prepared operational evidence could not be read.'
    assert tuple(group.group for group in model.groups) == OPERATIONAL_STATUS_GROUP_ORDER


def test_operational_status_view_model_and_evidence_are_immutable():
    model = build_operational_status_view_model(
        evidence=(
            _evidence('local_authority', 'Local runtime authority is present.'),
        )
    )

    with pytest.raises(FrozenInstanceError):
        model.headline = 'Changed'

    with pytest.raises(FrozenInstanceError):
        model.groups[0].detail = 'Changed'


@pytest.mark.parametrize(
    ('builder', 'exception'),
    [
        (
            lambda: build_operational_status_view_model(evidence=[]),
            TypeError,
        ),
        (
            lambda: build_operational_status_view_model(
                evidence=(
                    _evidence('local_authority', 'one'),
                    _evidence('local_authority', 'two'),
                )
            ),
            ValueError,
        ),
        (
            lambda: build_operational_status_view_model(error_text='  '),
            ValueError,
        ),
        (
            lambda: operational_status_evidence(
                'unknown', state='available', detail='unsupported'
            ),
            ValueError,
        ),
        (
            lambda: operational_status_evidence(
                'inventory', state='live', detail='unsupported'
            ),
            ValueError,
        ),
        (
            lambda: operational_status_evidence(
                'inventory', state='available', detail=' '
            ),
            ValueError,
        ),
        (
            lambda: operational_status_evidence(
                'inventory',
                state='available',
                detail='Inventory is available.',
                label=' ',
            ),
            ValueError,
        ),
    ],
)
def test_operational_status_view_model_rejects_invalid_inputs(
    builder, exception
) -> None:
    with pytest.raises(exception):
        builder()
