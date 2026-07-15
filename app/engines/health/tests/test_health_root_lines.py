import pytest

from app.engines.health.application_adapter import HealthApplicationBoundary
from app.engines.health.bundle import create_health_provider_bundle
from app.engines.health.provider import HealthReportProvider
from app.engines.health.result import HealthResult, HealthStatus
from app.engines.health.root_lines import health_root_lines
from app.engines.health.root_registration import HealthRootRegistration
from app.engines.health.root_registry import register_health_root
from app.engines.health.runtime import HealthRuntimeComposition
from app.engines.health.summary import summarize_health_results


def _summary(status: HealthStatus):
    return summarize_health_results(
        [HealthResult('database', status, 'database summary', '2026-07-15T00:45:00Z')]
    )


def _registered_root():
    bundle = create_health_provider_bundle(
        [
            HealthReportProvider('application', lambda: _summary(HealthStatus.PASS)),
            HealthReportProvider('database', lambda: _summary(HealthStatus.WARN)),
        ]
    )
    composition = HealthRuntimeComposition('MarketDEX', bundle)
    boundary = HealthApplicationBoundary('desktop', composition)
    return register_health_root(HealthRootRegistration('desktop-health', boundary))


def test_health_root_lines_has_exact_deterministic_tuple() -> None:
    assert health_root_lines(_registered_root()) == (
        'registration=desktop-health',
        'boundary=desktop',
        'runtime=MarketDEX',
        'overall=WARN',
        'providers=2',
        'provider=application:PASS:findings=0',
        'provider=database:WARN:findings=1',
    )


def test_health_root_lines_preserves_registration_and_application_order() -> None:
    lines = health_root_lines(_registered_root())

    assert lines[0] == 'registration=desktop-health'
    assert lines[1:] == (
        'boundary=desktop',
        'runtime=MarketDEX',
        'overall=WARN',
        'providers=2',
        'provider=application:PASS:findings=0',
        'provider=database:WARN:findings=1',
    )


def test_health_root_lines_rejects_invalid_registered_root() -> None:
    with pytest.raises(TypeError, match='registered_root must be a RegisteredHealthRoot'):
        health_root_lines(object())
