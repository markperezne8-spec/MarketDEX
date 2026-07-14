from __future__ import annotations

from .findings import health_findings
from .result import HealthStatus
from .summary import HealthSummary


def health_report_lines(summary: HealthSummary) -> tuple[str, ...]:
    if not isinstance(summary, HealthSummary):
        raise TypeError('summary must be a HealthSummary')

    lines = [
        f'overall={summary.overall_status.value}',
        'counts=' + ','.join(f'{status.value}:{summary.counts[status]}' for status in sorted(HealthStatus, key=lambda status: status.value)),
    ]

    findings = health_findings(summary)
    if not findings:
        lines.append('findings=none')
        return tuple(lines)

    lines.append(f'findings={len(findings)}')
    lines.extend(
        f'finding={finding.status.value}:{finding.check_name}:{finding.summary}'
        for finding in findings
    )
    return tuple(lines)
