from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from .envelope import EventEnvelope

EventHandler = Callable[[EventEnvelope], None]


class InMemoryEventBus:
    """Deterministic in-memory event delivery with subscriber isolation."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> Callable[[], None]:
        if not event_name.strip():
            raise ValueError('event_name must be non-empty text')
        if not callable(handler):
            raise TypeError('handler must be callable')
        self._handlers[event_name].append(handler)

        def unsubscribe() -> None:
            handlers = self._handlers.get(event_name, [])
            if handler in handlers:
                handlers.remove(handler)
            if not handlers:
                self._handlers.pop(event_name, None)

        return unsubscribe

    def publish(self, envelope: EventEnvelope) -> tuple[BaseException, ...]:
        if not isinstance(envelope, EventEnvelope):
            raise TypeError('envelope must be an EventEnvelope')
        failures: list[BaseException] = []
        for handler in tuple(self._handlers.get(envelope.event_name, ())):
            try:
                handler(envelope)
            except BaseException as exc:
                failures.append(exc)
        return tuple(failures)
