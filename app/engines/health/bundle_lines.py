from __future__ import annotations

from .bundle import HealthProviderBundle
from .bundle_summary import health_bundle_summary


def health_bundle_report_lines(bundle: HealthProviderBundle) -> tuple[str, ...]:
    if not isinstance(bundle, HealthProviderBundle):
        raise TypeError('bundle must be a HealthProviderBundle')

    summary = health_bundle_summary(bundle)
    lines = [
        f"overall={summary['overall_status']}",
        f"providers={summary['provider_count']}",
    ]
    if not summary['providers']:
        lines.append('provider_statuses=none')
        return tuple(lines)

    lines.extend(
        f"provider={provider['name']}:{provider['overall_status']}:findings={provider['finding_count']}"
        for provider in summary['providers']
    )
    return tuple(lines)
