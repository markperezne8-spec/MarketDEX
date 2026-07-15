import pytest

from app.engines.health.application_adapter import HealthApplicationBoundary
from app.engines.health.application_payload import health_application_payload
from app.engines.health.bundle import create_health_provider_bundle
from app.engines.health.provider import HealthReportProvider
from app.engines.health.result import HealthResult
from app.engines.health.runtime import HealthRuntimeComposition
from app.engines.health.result import HealthStatus
from app.engines.health.summary import summarize_health_results


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


def test_health_application_payload_preserves_boundary_and_provider_order() -> None:
    payload = health_application_payload(_boundary())

    assert payload['boundary'] == 'desktop'
    assert payload['runtime']['runtime'] == 'MarketDEX'
    assert [
        report['provider'] for report in payload['runtime']['health']['reports']
    ] == ['application', 'database']


def test_health_application_payload_rejects_invalid_boundary() -> None:
    with pytest.raises(TypeError):
        health_application_payload(object())
