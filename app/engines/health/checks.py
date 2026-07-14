from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .result import HealthResult, validate_health_result
from .summary import HealthSummary, summarize_health_results


@dataclass(frozen=True, slots=True)
class HealthCheck:
    name: str
    run: Callable[[], HealthResult]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError('name must be non-empty text')
        if not callable(self.run):
            raise TypeError('run must be callable')


def run_health_checks(checks: Iterable[HealthCheck]) -> HealthSummary:
    results: list[HealthResult] = []

    for check in checks:
        if not isinstance(check, HealthCheck):
            raise TypeError('checks must contain HealthCheck values')

        result = check.run()
        validate_health_result(result)
        if result.check_name != check.name:
            raise ValueError('health check result name must match the registered check name')
        results.append(result)

    return summarize_health_results(results)
