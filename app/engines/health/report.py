from __future__ import annotations

from typing import Any

from .findings import health_findings
from .snapshot import health_summary_snapshot
from .summary import HealthSummary


def health_report_payload(summary: HealthSummary) -> dict[str, Any]:
    if not isinstance(summary, HealthSummary):
        raise TypeError('summary must be a HealthSummary')

    return {
        'health': health_summary_snapshot(summary),
        'findings': [
            {
                'check_name': finding.check_name,
                'status': finding.status.value,
                'summary': finding.summary,
                'remediation': finding.remediation,
            }
            for finding in health_findings(summary)
        ],
    }
