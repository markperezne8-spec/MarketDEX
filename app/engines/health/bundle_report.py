from __future__ import annotations

from typing import Any

from .bundle import HealthProviderBundle, build_health_reports
from .bundle_summary import health_bundle_summary


def health_bundle_report_payload(bundle: HealthProviderBundle) -> dict[str, Any]:
    if not isinstance(bundle, HealthProviderBundle):
        raise TypeError('bundle must be a HealthProviderBundle')

    return {
        'summary': health_bundle_summary(bundle),
        'reports': list(build_health_reports(bundle)),
    }
