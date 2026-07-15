import pytest

from app.engines.health.application_adapter import (
    HealthApplicationBoundary,
    adapt_health_application_request,
)
from app.engines.health.application_request import HealthApplicationRequest
from app.engines.health.bundle import create_health_provider_bundle
from app.engines.health.runtime import HealthRuntimeComposition


def _request() -> HealthApplicationRequest:
    composition = HealthRuntimeComposition(
        'MarketDEX',
        create_health_provider_bundle([]),
    )
    return HealthApplicationRequest('application-health', composition)


def test_adapt_health_application_request_preserves_boundary_and_composition() -> None:
    request = _request()

    boundary = adapt_health_application_request(request)

    assert boundary == HealthApplicationBoundary(
        boundary_name='application-health',
        composition=request.composition,
    )
    assert boundary.composition is request.composition


def test_health_application_boundary_is_immutable() -> None:
    boundary = adapt_health_application_request(_request())

    with pytest.raises(AttributeError):
        boundary.boundary_name = 'other'


def test_adapt_health_application_request_rejects_invalid_request() -> None:
    with pytest.raises(TypeError):
        adapt_health_application_request(object())
