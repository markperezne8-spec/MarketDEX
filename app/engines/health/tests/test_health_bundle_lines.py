import pytest

from app.engines.health import (
    HealthReportProvider,
    HealthResult,
    HealthStatus,
    create_health_provider_bundle,
    health_bundle_report_lines,
    summarize_health_results,
)


def _summary(status: HealthStatus, name: str = 'database'):
    return summarize_health_results(
        [HealthResult(name, status, f'{name} summary', '2026-07-15T00:30:00Z')]
    )


def test_health_bundle_report_lines_empty_bundle() -> None:
    bundle = create_health_provider_bundle([])

    lines = health_bundle_report_lines(bundle)

    assert lines == (
        'overall=UNKNOWN',
        'providers=0',
        'provider_statuses=none',
    )


def test_health_bundle_report_lines_preserves_provider_order() -> None:
    bundle = create_health_provider_bundle(
        [
            HealthReportProvider('application', lambda: _summary(HealthStatus.PASS)),
            HealthReportProvider('database', lambda: _summary(HealthStatus.WARN)),
            HealthReportProvider('brokerage', lambda: _summary(HealthStatus.FAIL)),
        ]
    )

    lines = health_bundle_report_lines(bundle)

    assert lines == (
        'overall=FAIL',
        'providers=3',
        'provider=application:PASS:findings=0',
        'provider=database:WARN:findings=1',
        'provider=brokerage:FAIL:findings=1',
    )


def test_health_bundle_report_lines_counts_unknown_as_finding() -> None:
    bundle = create_health_provider_bundle(
        [HealthReportProvider('application', lambda: _summary(HealthStatus.UNKNOWN))]
    )

    lines = health_bundle_report_lines(bundle)

    assert lines == (
        'overall=UNKNOWN',
        'providers=1',
        'provider=application:UNKNOWN:findings=1',
    )


def test_health_bundle_report_lines_rejects_invalid_bundle() -> None:
    with pytest.raises(TypeError):
        health_bundle_report_lines(object())
