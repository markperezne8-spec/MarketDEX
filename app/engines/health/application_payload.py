from __future__ import annotations

from typing import Any

from .application_adapter import HealthApplicationBoundary
from .runtime import build_runtime_health_report


def health_application_payload(boundary: HealthApplicationBoundary) -> dict[str, Any]:
    if not isinstance(boundary, HealthApplicationBoundary):
        raise TypeError('boundary must be a HealthApplicationBoundary')

    return {
        'boundary': boundary.boundary_name,
        'runtime': build_runtime_health_report(boundary.composition),
    }
