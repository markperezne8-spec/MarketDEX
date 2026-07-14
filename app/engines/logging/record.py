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
        if not self.timestamp or not self.component or not self.event or not self.message:
            raise ValueError('timestamp, component, event, and message are required')
        if self.correlation_id == '':
            raise ValueError('correlation_id must be non-empty when provided')
        if not isinstance(self.details, Mapping):
            raise TypeError('details must be a mapping')
        object.__setattr__(self, 'details', MappingProxyType(dict(self.details)))


def validate_log_record(record: LogRecord) -> bool:
    if not isinstance(record, LogRecord):
        raise TypeError('record must be a LogRecord')
    return True
