from __future__ import annotations

from dataclasses import dataclass

from .application_adapter import HealthApplicationBoundary


@dataclass(frozen=True, slots=True)
class HealthRootRegistration:
    registration_name: str
    boundary: HealthApplicationBoundary

    def __post_init__(self) -> None:
        if not isinstance(self.registration_name, str) or not self.registration_name.strip():
            raise ValueError('registration_name must be non-empty text')
        if not isinstance(self.boundary, HealthApplicationBoundary):
            raise TypeError('boundary must be a HealthApplicationBoundary')
