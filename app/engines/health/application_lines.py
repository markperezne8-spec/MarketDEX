from __future__ import annotations

from .application_adapter import HealthApplicationBoundary
from .runtime import runtime_health_report_lines


def health_application_lines(boundary: HealthApplicationBoundary) -> tuple[str, ...]:
    if not isinstance(boundary, HealthApplicationBoundary):
        raise TypeError('boundary must be a HealthApplicationBoundary')

    return (
        f'boundary={boundary.boundary_name}',
        *runtime_health_report_lines(boundary.composition),
    )
