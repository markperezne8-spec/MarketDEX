from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .result import HealthResult, HealthStatus
from .summary import HealthSummary


_FINDING_ORDER = {
    HealthStatus.FAIL: 0,
    HealthStatus.WARN: 1,
    HealthStatus.UNKNOWN: 2,
}


@dataclass(frozen=True, slots=True)
class HealthFinding:
    check_name: str
    status: HealthStatus
    summary: str
    remediation: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.check_name, str) or not self.check_name.strip():
            raise ValueError('check_name must be non-empty text')
        if not isinstance(self.status, HealthStatus):
            raise TypeError('status must be a HealthStatus')
        if self.status is HealthStatus.PASS:
            raise ValueError('findings cannot be created for passing health results')
        if not isinstance(self.summary, str) or not self.summary.strip():
            raise ValueError('summary must be non-empty text')
        if self.remediation is not None and not self.remediation.strip():
            raise ValueError('remediation must be non-empty text when provided')


def health_findings(summary: HealthSummary) -> tuple[HealthFinding, ...]:
    if not isinstance(summary, HealthSummary):
        raise TypeError('summary must be a HealthSummary')

    findings = [_finding_from_result(result) for result in summary.results if result.status is not HealthStatus.PASS]
    return tuple(sorted(findings, key=lambda finding: (_FINDING_ORDER[finding.status], finding.check_name)))


def _finding_from_result(result: HealthResult) -> HealthFinding:
    return HealthFinding(
        check_name=result.check_name,
        status=result.status,
        summary=result.summary,
        remediation=result.remediation,
    )
