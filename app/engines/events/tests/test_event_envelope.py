import pytest

from app.engines.events import EventEnvelope


def test_event_envelope_detaches_and_freezes_payload() -> None:
    payload = {'item': {'status': 'ready'}, 'tags': ['a', 'b']}

    envelope = EventEnvelope(
        event_name='inventory.updated',
        occurred_at='2026-07-14T22:00:00Z',
        source='inventory',
        payload=payload,
        correlation_id='op-1',
    )

    payload['item']['status'] = 'changed'

    assert envelope.payload['item']['status'] == 'ready'
    assert envelope.payload['tags'] == ('a', 'b')
    with pytest.raises(TypeError):
        envelope.payload['item']['status'] = 'blocked'


def test_event_envelope_rejects_missing_identity() -> None:
    with pytest.raises(ValueError):
        EventEnvelope('', '2026-07-14T22:00:00Z', 'inventory', {})


def test_event_envelope_requires_mapping_payload() -> None:
    with pytest.raises(TypeError):
        EventEnvelope('inventory.updated', '2026-07-14T22:00:00Z', 'inventory', [])


def test_event_envelope_rejects_blank_correlation_id() -> None:
    with pytest.raises(ValueError):
        EventEnvelope('inventory.updated', '2026-07-14T22:00:00Z', 'inventory', {}, ' ')
