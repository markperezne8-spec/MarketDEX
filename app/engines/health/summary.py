from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping

from .result import HealthResult, HealthStatus, validate_health_result


_STATUS_PRECEDENCE = {
    HealthStatus.PASS: 0,
    HealthStatus.UNKNOWN: 1,
    HealthStatus.WARN: 2,
    HealthStatus.FAIL: 3,
}


@dataclass(frozen=True, slots=True)
class HealthSummary:
    overall_status: HealthStatus
    results: tuple[HealthResult, ...]
    counts: Mapping[HealthStatus, int]

    def __post_init__(self) -> None:
        if not isinstance(self.overall_status, HealthStatus):
            raise TypeError('overall_status must be a HealthStatus')
        if not isinstance(self.results, tuple):
            raise TypeError('results must be a tuple of HealthResult values')
        for result in self.results:
            validate_health_result(result)
        if set(self.counts) != set(HealthStatus):
            raise ValueError('counts must include every HealthStatus')
        if any(not isinstance(count, int) or count < 0 for count in self.counts.values()):
            raise ValueError('counts must be non-negative integers')
        object.__setattr__(self, 'counts', MappingProxyType(dict(self.counts)))


def summarize_health_results(results: Iterable[HealthResult]) -> HealthSummary:
    normalized_results = tuple(results)
    counts = {status: 0 for status in HealthStatus}

    for result in normalized_results:
        validate_health_result(result)
        counts[result.status] += 1

    overall_status = max(
        (result.status for result in normalized_results),
        key=lambda status: _STATUS_PRECEDENCE[status],
        default=HealthStatus.UNKNOWN,
    )

    return HealthSummary(overall_status, normalized_results, counts)
