from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class HealthStatus(StrEnum):
    PASS = 'PASS'
    WARN = 'WARN'
    FAIL = 'FAIL'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True, slots=True)
class HealthResult:
    check_name: str
    status: HealthStatus
    summary: str
    checked_at: str
    details: Mapping[str, Any] = MappingProxyType({})
    remediation: str | None = None

    def __post_init__(self) -> None:
        required = {
            'check_name': self.check_name,
            'summary': self.summary,
            'checked_at': self.checked_at,
        }
        if any(not isinstance(value, str) or not value.strip() for value in required.values()):
            raise ValueError('check_name, summary, and checked_at must be non-empty text')
        if not isinstance(self.status, HealthStatus):
            raise TypeError('status must be a HealthStatus')
        if self.remediation is not None and not self.remediation.strip():
            raise ValueError('remediation must be non-empty text when provided')
        if not isinstance(self.details, Mapping):
            raise TypeError('details must be a mapping')
        object.__setattr__(
            self,
            'details',
            MappingProxyType(deepcopy(dict(self.details))),
        )


def validate_health_result(result: HealthResult) -> bool:
    if not isinstance(result, HealthResult):
        raise TypeError('result must be a HealthResult')
    return True
