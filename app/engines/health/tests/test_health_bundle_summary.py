import pytest

from app.engines.health import (
    HealthReportProvider,
    HealthResult,
    HealthStatus,
    create_health_provider_bundle,
    health_bundle_summary,
    summarize_health_results,
)


def _summary(status: HealthStatus, name: str = 'database'):
    return summarize_health_results(
        [HealthResult(name, status, f'{name} summary', '2026-07-15T00:20:00Z')]
    )


def test_health_bundle_summary_empty_bundle_is_unknown() -> None:
    bundle = create_health_provider_bundle([])

    summary = health_bundle_summary(bundle)

    assert summary == {
        'overall_status': 'UNKNOWN',
        'provider_count': 0,
        'providers': [],
    }


def test_health_bundle_summary_aggregates_highest_provider_status() -> None:
    bundle = create_health_provider_bundle(
        [
            HealthReportProvider('application', lambda: _summary(HealthStatus.PASS)),
            HealthReportProvider('database', lambda: _summary(HealthStatus.WARN)),
            HealthReportProvider('brokerage', lambda: _summary(HealthStatus.FAIL)),
        ]
    )

    summary = health_bundle_summary(bundle)

    assert summary['overall_status'] == 'FAIL'


def test_health_bundle_summary_preserves_provider_order_and_finding_counts() -> None:
    bundle = create_health_provider_bundle(
        [
            HealthReportProvider('application', lambda: _summary(HealthStatus.PASS)),
            HealthReportProvider('database', lambda: _summary(HealthStatus.WARN)),
        ]
    )

    summary = health_bundle_summary(bundle)

    assert summary['providers'] == [
        {'name': 'application', 'overall_status': 'PASS', 'finding_count': 0},
        {'name': 'database', 'overall_status': 'WARN', 'finding_count': 1},
    ]


def test_health_bundle_summary_rejects_invalid_bundle() -> None:
    with pytest.raises(TypeError):
        health_bundle_summary(object())
