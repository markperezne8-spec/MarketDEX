from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from .report import health_report_payload
from .summary import HealthSummary


@dataclass(frozen=True, slots=True)
class HealthReportProvider:
    name: str
    collect: Callable[[], HealthSummary]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError('name must be non-empty text')
        if not callable(self.collect):
            raise TypeError('collect must be callable')


def build_health_report(provider: HealthReportProvider) -> dict[str, Any]:
    if not isinstance(provider, HealthReportProvider):
        raise TypeError('provider must be a HealthReportProvider')

    summary = provider.collect()
    if not isinstance(summary, HealthSummary):
        raise TypeError('provider collect must return a HealthSummary')

    return health_report_payload(summary)
