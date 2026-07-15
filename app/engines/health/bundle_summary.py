from __future__ import annotations

from typing import Any

from .bundle import HealthProviderBundle, build_health_reports
from .result import HealthStatus


_STATUS_PRECEDENCE = {
    HealthStatus.PASS: 0,
    HealthStatus.UNKNOWN: 1,
    HealthStatus.WARN: 2,
    HealthStatus.FAIL: 3,
}


def health_bundle_summary(bundle: HealthProviderBundle) -> dict[str, Any]:
    if not isinstance(bundle, HealthProviderBundle):
        raise TypeError('bundle must be a HealthProviderBundle')

    reports = build_health_reports(bundle)
    provider_statuses = [
        HealthStatus(entry['report']['health']['overall_status'])
        for entry in reports
    ]
    overall_status = max(
        provider_statuses,
        key=lambda status: _STATUS_PRECEDENCE[status],
        default=HealthStatus.UNKNOWN,
    )

    return {
        'overall_status': overall_status.value,
        'provider_count': len(reports),
        'providers': [
            {
                'name': entry['provider'],
                'overall_status': entry['report']['health']['overall_status'],
                'finding_count': len(entry['report']['findings']),
            }
            for entry in reports
        ],
    }
