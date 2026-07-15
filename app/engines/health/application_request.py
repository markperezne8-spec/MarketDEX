from __future__ import annotations

from dataclasses import dataclass

from .runtime import HealthRuntimeComposition


@dataclass(frozen=True, slots=True)
class HealthApplicationRequest:
    boundary_name: str
    composition: HealthRuntimeComposition

    def __post_init__(self) -> None:
        if not isinstance(self.boundary_name, str) or not self.boundary_name.strip():
            raise ValueError('boundary_name must be non-empty text')
        if not isinstance(self.composition, HealthRuntimeComposition):
            raise TypeError('composition must be a HealthRuntimeComposition')
