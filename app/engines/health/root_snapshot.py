from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .application_payload import health_application_payload
from .root_registry import RegisteredHealthRoot


@dataclass(frozen=True, slots=True)
class HealthRootSnapshot:
    registration_name: str
    payload: dict[str, Any]


def snapshot_health_root(registered_root: RegisteredHealthRoot) -> HealthRootSnapshot:
    if not isinstance(registered_root, RegisteredHealthRoot):
        raise TypeError('registered_root must be a RegisteredHealthRoot')

    return HealthRootSnapshot(
        registration_name=registered_root.registration_name,
        payload=health_application_payload(registered_root.boundary),
    )
