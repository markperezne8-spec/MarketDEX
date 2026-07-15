from __future__ import annotations

from typing import Any

from .application_payload import health_application_payload
from .root_registry import RegisteredHealthRoot


def health_root_payload(registered_root: RegisteredHealthRoot) -> dict[str, Any]:
    if not isinstance(registered_root, RegisteredHealthRoot):
        raise TypeError('registered_root must be a RegisteredHealthRoot')

    return {
        'registration_name': registered_root.registration_name,
        'application': health_application_payload(registered_root.boundary),
    }
