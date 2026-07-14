from __future__ import annotations

from copy import deepcopy
from typing import Any

from .summary import HealthSummary


def health_summary_snapshot(summary: HealthSummary) -> dict[str, Any]:
    if not isinstance(summary, HealthSummary):
        raise TypeError('summary must be a HealthSummary')

    return {
        'overall_status': summary.overall_status.value,
        'counts': {
            status.value: summary.counts[status]
            for status in sorted(summary.counts, key=lambda status: status.value)
        },
        'results': [
            {
                'check_name': result.check_name,
                'status': result.status.value,
                'summary': result.summary,
                'checked_at': result.checked_at,
                'details': deepcopy(dict(result.details)),
                'remediation': result.remediation,
            }
            for result in summary.results
        ],
    }
