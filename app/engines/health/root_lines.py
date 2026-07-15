from __future__ import annotations

from .application_lines import health_application_lines
from .root_registry import RegisteredHealthRoot


def health_root_lines(registered_root: RegisteredHealthRoot) -> tuple[str, ...]:
    if not isinstance(registered_root, RegisteredHealthRoot):
        raise TypeError('registered_root must be a RegisteredHealthRoot')

    return (
        f'registration={registered_root.registration_name}',
        *health_application_lines(registered_root.boundary),
    )
