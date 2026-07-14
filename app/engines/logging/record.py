from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class LogLevel(StrEnum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


@dataclass(frozen=True, slots=True)
class LogRecord:
    timestamp: str
    level: LogLevel
    component: str
    event: str
    message: str
    correlation_id: str | None = None
    details: Mapping[str, Any] = MappingProxyType({})

    def __post_init__(self) -> None:
        if not isinstance(self.level, LogLevel):
            raise TypeError('level must be a LogLevel')
        required = {
            'timestamp': self.timestamp,
            'component': self.component,
            'event': self.event,
            'message': self.message,
        }
        if any(not isinstance(value, str) or not value.strip() for value in required.values()):
            raise ValueError('timestamp, component, event, and message must be non-empty text')
        if self.correlation_id is not None and (
            not isinstance(self.correlation_id, str) or not self.correlation_id.strip()
        ):
            raise ValueError('correlation_id must be non-empty text when provided')
        if not isinstance(self.details, Mapping):
            raise TypeError('details must be a mapping')
        if any(not isinstance(key, str) or not key.strip() for key in self.details):
            raise ValueError('detail keys must be non-empty text')
        object.__setattr__(self, 'details', MappingProxyType(dict(self.details)))


def validate_log_record(record: LogRecord) -> bool:
    if not isinstance(record, LogRecord):
        raise TypeError('record must be a LogRecord')
    return True
