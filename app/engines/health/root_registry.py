from __future__ import annotations

from dataclasses import dataclass

from .application_adapter import HealthApplicationBoundary
from .root_registration import HealthRootRegistration


@dataclass(frozen=True, slots=True)
class RegisteredHealthRoot:
    registration_name: str
    boundary: HealthApplicationBoundary


def register_health_root(
    registration: HealthRootRegistration,
) -> RegisteredHealthRoot:
    if not isinstance(registration, HealthRootRegistration):
        raise TypeError('registration must be a HealthRootRegistration')

    return RegisteredHealthRoot(
        registration_name=registration.registration_name,
        boundary=registration.boundary,
    )
