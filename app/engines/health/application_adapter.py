from __future__ import annotations

from dataclasses import dataclass

from .application_request import HealthApplicationRequest
from .runtime import HealthRuntimeComposition


@dataclass(frozen=True, slots=True)
class HealthApplicationBoundary:
    boundary_name: str
    composition: HealthRuntimeComposition


def adapt_health_application_request(
    request: HealthApplicationRequest,
) -> HealthApplicationBoundary:
    if not isinstance(request, HealthApplicationRequest):
        raise TypeError('request must be a HealthApplicationRequest')

    return HealthApplicationBoundary(
        boundary_name=request.boundary_name,
        composition=request.composition,
    )
