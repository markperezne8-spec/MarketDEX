import pytest

from app.engines.health import (
    HealthReportProvider,
    HealthResult,
    HealthStatus,
    build_health_report,
    summarize_health_results,
)


def _summary():
    return summarize_health_results(
        [HealthResult('database', HealthStatus.PASS, 'database summary', '2026-07-15T00:10:00Z')]
    )


def test_health_report_provider_is_immutable() -> None:
    provider = HealthReportProvider('application', _summary)

    with pytest.raises(AttributeError):
        provider.name = 'changed'


def test_build_health_report_invokes_provider_and_returns_payload() -> None:
    calls: list[str] = []

    def collect():
        calls.append('collect')
        return _summary()

    provider = HealthReportProvider('application', collect)

    report = build_health_report(provider)

    assert calls == ['collect']
    assert report['health']['overall_status'] == 'PASS'
    assert report['findings'] == []


def test_health_report_provider_rejects_invalid_name() -> None:
    with pytest.raises(ValueError):
        HealthReportProvider('', _summary)


def test_health_report_provider_rejects_non_callable_collect() -> None:
    with pytest.raises(TypeError):
        HealthReportProvider('application', object())


def test_build_health_report_rejects_invalid_provider() -> None:
    with pytest.raises(TypeError):
        build_health_report(object())


def test_build_health_report_rejects_invalid_provider_result() -> None:
    provider = HealthReportProvider('application', lambda: object())

    with pytest.raises(TypeError):
        build_health_report(provider)
