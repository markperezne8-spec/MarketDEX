import pytest

from app.engines.health import (
    HealthApplicationBoundary,
    HealthReportProvider,
    HealthResult,
    HealthRuntimeComposition,
    HealthStatus,
    create_health_provider_bundle,
    health_application_lines,
    summarize_health_results,
)


def _summary(status: HealthStatus):
    return summarize_health_results(
        [HealthResult('database', status, 'database summary', '2026-07-15T00:45:00Z')]
    )


def _boundary() -> HealthApplicationBoundary:
    bundle = create_health_provider_bundle(
        [
            HealthReportProvider('application', lambda: _summary(HealthStatus.PASS)),
            HealthReportProvider('database', lambda: _summary(HealthStatus.WARN)),
        ]
    )
    composition = HealthRuntimeComposition('MarketDEX', bundle)
    return HealthApplicationBoundary('desktop', composition)


def test_health_application_lines_preserve_boundary_runtime_and_provider_order() -> None:
    assert health_application_lines(_boundary()) == (
        'boundary=desktop',
        'runtime=MarketDEX',
        'overall=WARN',
        'providers=2',
        'provider=application:PASS:findings=0',
        'provider=database:WARN:findings=1',
    )


def test_health_application_lines_reject_invalid_boundary() -> None:
    with pytest.raises(TypeError):
        health_application_lines(object())
