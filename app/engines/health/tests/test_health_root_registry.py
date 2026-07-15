from dataclasses import FrozenInstanceError

import pytest

from app.engines.health.application_adapter import HealthApplicationBoundary
from app.engines.health.root_registration import HealthRootRegistration
from app.engines.health.root_registry import RegisteredHealthRoot, register_health_root
from app.engines.health.runtime import HealthRuntimeComposition


def _boundary() -> HealthApplicationBoundary:
    composition = object.__new__(HealthRuntimeComposition)
    object.__setattr__(composition, 'runtime_name', 'desktop')
    object.__setattr__(composition, 'provider_bundle', object())
    return HealthApplicationBoundary('health', composition)


def test_register_health_root_preserves_exact_identity() -> None:
    boundary = _boundary()
    registration = HealthRootRegistration('primary', boundary)

    registered = register_health_root(registration)

    assert registered.registration_name == 'primary'
    assert registered.boundary is boundary
    assert registered.boundary.composition is boundary.composition


def test_registered_health_root_is_immutable() -> None:
    registered = register_health_root(HealthRootRegistration('primary', _boundary()))

    with pytest.raises(FrozenInstanceError):
        registered.registration_name = 'secondary'


def test_register_health_root_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match='registration must be a HealthRootRegistration'):
        register_health_root(object())


def test_registered_health_root_contract_is_exact() -> None:
    registered = register_health_root(HealthRootRegistration('primary', _boundary()))

    assert isinstance(registered, RegisteredHealthRoot)
