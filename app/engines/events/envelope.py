from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_name: str
    occurred_at: str
    source: str
    payload: Mapping[str, Any]
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        required = {
            'event_name': self.event_name,
            'occurred_at': self.occurred_at,
            'source': self.source,
        }
        if any(not isinstance(value, str) or not value.strip() for value in required.values()):
            raise ValueError('event_name, occurred_at, and source must be non-empty text')
        if self.correlation_id is not None and (
            not isinstance(self.correlation_id, str) or not self.correlation_id.strip()
        ):
            raise ValueError('correlation_id must be non-empty text when provided')
        if not isinstance(self.payload, Mapping):
            raise TypeError('payload must be a mapping')
        source = deepcopy(dict(self.payload))
        object.__setattr__(self, 'payload', _freeze(source))


def validate_event_envelope(envelope: EventEnvelope) -> bool:
    if not isinstance(envelope, EventEnvelope):
        raise TypeError('envelope must be an EventEnvelope')
    return True
