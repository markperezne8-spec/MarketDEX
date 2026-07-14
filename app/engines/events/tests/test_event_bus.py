import pytest

from app.engines.events import EventEnvelope, InMemoryEventBus


def envelope() -> EventEnvelope:
    return EventEnvelope('inventory.updated', '2026-07-14T22:00:00Z', 'inventory', {'id': 1})


def test_publish_delivers_in_subscription_order() -> None:
    bus = InMemoryEventBus()
    received: list[str] = []

    bus.subscribe('inventory.updated', lambda event: received.append('first'))
    bus.subscribe('inventory.updated', lambda event: received.append('second'))

    assert bus.publish(envelope()) == ()
    assert received == ['first', 'second']


def test_publish_isolates_subscriber_failures() -> None:
    bus = InMemoryEventBus()
    received: list[str] = []

    def failing(event: EventEnvelope) -> None:
        raise RuntimeError('subscriber failed')

    bus.subscribe('inventory.updated', failing)
    bus.subscribe('inventory.updated', lambda event: received.append('after-failure'))

    failures = bus.publish(envelope())

    assert len(failures) == 1
    assert isinstance(failures[0], RuntimeError)
    assert received == ['after-failure']


def test_unsubscribe_is_deterministic_and_idempotent() -> None:
    bus = InMemoryEventBus()
    received: list[int] = []
    unsubscribe = bus.subscribe('inventory.updated', lambda event: received.append(1))

    unsubscribe()
    unsubscribe()

    assert bus.publish(envelope()) == ()
    assert received == []


def test_subscribe_rejects_invalid_inputs() -> None:
    bus = InMemoryEventBus()
    with pytest.raises(ValueError):
        bus.subscribe(' ', lambda event: None)
    with pytest.raises(TypeError):
        bus.subscribe('inventory.updated', object())
