import pytest

from app.engines.health import (
    HealthReportProvider,
    HealthResult,
    HealthRuntimeComposition,
    HealthStatus,
    create_health_provider_bundle,
    summarize_health_results,
)
from app.engines.health.application_request import HealthApplicationRequest


def _composition() -> HealthRuntimeComposition:
    summary = summarize_health_results(
        [HealthResult('application', HealthStatus.PASS, 'ready', '2026-07-15T01:30:00Z')]
    )
    bundle = create_health_provider_bundle(
        [HealthReportProvider('application', lambda: summary)]
    )
    return HealthRuntimeComposition('MarketDEX', bundle)


def test_health_application_request_preserves_boundary_and_composition() -> None:
    composition = _composition()

    request = HealthApplicationRequest('mission-control', composition)

    assert request.boundary_name == 'mission-control'
    assert request.composition is composition


def test_health_application_request_is_immutable() -> None:
    request = HealthApplicationRequest('mission-control', _composition())

    with pytest.raises(AttributeError):
        request.boundary_name = 'other'


def test_health_application_request_rejects_blank_boundary_name() -> None:
    with pytest.raises(ValueError):
        HealthApplicationRequest('  ', _composition())


def test_health_application_request_rejects_invalid_composition() -> None:
    with pytest.raises(TypeError):
        HealthApplicationRequest('mission-control', object())
