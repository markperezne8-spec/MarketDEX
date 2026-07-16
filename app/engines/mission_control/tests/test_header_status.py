from dataclasses import FrozenInstanceError

import pytest

from app.engines.mission_control.header_status import (
    HEADER_STATUS_SLOT_ORDER,
    HeaderStatusEvidence,
    HeaderStatusViewModel,
    build_header_status_view_model,
    header_status_evidence,
)


def _evidence(slot: str, detail: str, state: str = 'ready'):
    return header_status_evidence(slot, state=state, detail=detail)


def test_build_header_status_view_model_preserves_slot_order():
    model = build_header_status_view_model(
        evidence=(
            _evidence('local_authority', 'Local authority is prepared.'),
            _evidence('workbook_health', 'Workbook health evidence is prepared.'),
            _evidence('data_freshness', 'Freshness evidence is prepared.'),
            _evidence('app_status', 'Offline-first app shell is prepared.'),
            _evidence('operating_context', 'Mission Control context is prepared.'),
        )
    )

    assert model == HeaderStatusViewModel(
        state='ready',
        headline='Header status ready',
        slots=(
            HeaderStatusEvidence(
                slot='operating_context',
                state='ready',
                label='Operating context',
                detail='Mission Control context is prepared.',
            ),
            HeaderStatusEvidence(
                slot='app_status',
                state='ready',
                label='App/offline status',
                detail='Offline-first app shell is prepared.',
            ),
            HeaderStatusEvidence(
                slot='data_freshness',
                state='ready',
                label='Data freshness',
                detail='Freshness evidence is prepared.',
            ),
            HeaderStatusEvidence(
                slot='workbook_health',
                state='ready',
                label='Workbook health',
                detail='Workbook health evidence is prepared.',
            ),
            HeaderStatusEvidence(
                slot='local_authority',
                state='ready',
                label='Local authority',
                detail='Local authority is prepared.',
            ),
        ),
    )
    assert tuple(slot.slot for slot in model.slots) == HEADER_STATUS_SLOT_ORDER


def test_missing_header_status_evidence_is_unavailable():
    model = build_header_status_view_model()

    assert model.state == 'unavailable'
    assert model.headline == 'Header status unavailable'
    assert tuple(slot.slot for slot in model.slots) == HEADER_STATUS_SLOT_ORDER
    assert all(slot.state == 'unavailable' for slot in model.slots)
    assert all(slot.detail == 'Evidence unavailable.' for slot in model.slots)


def test_missing_and_partial_header_status_evidence_produce_partial_state():
    model = build_header_status_view_model(
        evidence=(
            _evidence('operating_context', 'Mission Control context is prepared.'),
            _evidence(
                'data_freshness',
                'Freshness contract is not approved yet.',
                'partial',
            ),
        )
    )

    assert model.state == 'partial'
    assert model.headline == 'Header status partially available'
    assert model.slots[0].state == 'ready'
    assert model.slots[1].state == 'unavailable'
    assert model.slots[2].state == 'partial'
    assert model.slots[3].state == 'unavailable'
    assert model.slots[4].state == 'unavailable'


def test_error_safe_header_status_preserves_injected_slots_inline():
    model = build_header_status_view_model(
        evidence=(
            _evidence('operating_context', 'Mission Control context is prepared.'),
        ),
        error_text='Prepared header status evidence could not be read.',
    )

    assert model.state == 'error'
    assert model.headline == 'Header status unavailable'
    assert model.error_text == 'Prepared header status evidence could not be read.'
    assert tuple(slot.slot for slot in model.slots) == HEADER_STATUS_SLOT_ORDER


def test_header_status_contract_is_immutable():
    model = build_header_status_view_model(
        evidence=(
            _evidence('operating_context', 'Mission Control context is prepared.'),
        )
    )

    with pytest.raises(FrozenInstanceError):
        model.headline = 'Changed'

    with pytest.raises(FrozenInstanceError):
        model.slots[0].detail = 'Changed'


@pytest.mark.parametrize(
    ('builder', 'exception'),
    [
        (lambda: build_header_status_view_model(evidence=[]), TypeError),
        (
            lambda: build_header_status_view_model(
                evidence=(
                    _evidence('operating_context', 'one'),
                    _evidence('operating_context', 'two'),
                )
            ),
            ValueError,
        ),
        (lambda: build_header_status_view_model(error_text=' '), ValueError),
        (
            lambda: header_status_evidence(
                'unknown', state='ready', detail='unsupported'
            ),
            ValueError,
        ),
        (
            lambda: header_status_evidence(
                'operating_context', state='live', detail='unsupported'
            ),
            ValueError,
        ),
        (
            lambda: header_status_evidence(
                'data_freshness', state='ready', detail=' '
            ),
            ValueError,
        ),
        (
            lambda: header_status_evidence(
                'workbook_health', state='ready', detail='Ready.', label=' '
            ),
            ValueError,
        ),
    ],
)
def test_header_status_rejects_invalid_inputs(builder, exception):
    with pytest.raises(exception):
        builder()
