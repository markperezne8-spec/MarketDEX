from dataclasses import FrozenInstanceError

import pytest

from app.engines.health.application_adapter import HealthApplicationBoundary
from app.engines.health.bundle import create_health_provider_bundle
from app.engines.health.root_registration import HealthRootRegistration
from app.engines.health.runtime import HealthRuntimeComposition


def _boundary() -> HealthApplicationBoundary:
    composition = HealthRuntimeComposition('MarketDEX', create_health_provider_bundle([]))
    return HealthApplicationBoundary('desktop', composition)


def test_health_root_registration_preserves_exact_boundary_identity() -> None:
    boundary = _boundary()

    registration = HealthRootRegistration('desktop-health', boundary)

    assert registration.registration_name == 'desktop-health'
    assert registration.boundary is boundary
    assert registration.boundary.composition is boundary.composition


def test_health_root_registration_is_immutable() -> None:
    registration = HealthRootRegistration('desktop-health', _boundary())

    with pytest.raises(FrozenInstanceError):
        registration.registration_name = 'changed'


def test_health_root_registration_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        HealthRootRegistration('   ', _boundary())


def test_health_root_registration_rejects_invalid_boundary() -> None:
    with pytest.raises(TypeError):
        HealthRootRegistration('desktop-health', object())
