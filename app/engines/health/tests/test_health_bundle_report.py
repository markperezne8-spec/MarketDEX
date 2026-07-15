import pytest

from app.engines.health import (
    HealthReportProvider,
    HealthResult,
    HealthStatus,
    create_health_provider_bundle,
    health_bundle_report_payload,
    summarize_health_results,
)


def _summary(status: HealthStatus, details: dict | None = None):
    return summarize_health_results(
        [HealthResult('database', status, 'database summary', '2026-07-15T00:25:00Z', details or {})]
    )


def test_health_bundle_report_payload_empty_bundle() -> None:
    bundle = create_health_provider_bundle([])

    payload = health_bundle_report_payload(bundle)

    assert payload == {
        'summary': {'overall_status': 'UNKNOWN', 'provider_count': 0, 'providers': []},
        'reports': [],
    }


def test_health_bundle_report_payload_preserves_provider_reports() -> None:
    bundle = create_health_provider_bundle(
        [
            HealthReportProvider('application', lambda: _summary(HealthStatus.PASS)),
            HealthReportProvider('database', lambda: _summary(HealthStatus.WARN)),
        ]
    )

    payload = health_bundle_report_payload(bundle)

    assert payload['summary']['overall_status'] == 'WARN'
    assert [report['provider'] for report in payload['reports']] == ['application', 'database']
    assert payload['reports'][0]['report']['health']['overall_status'] == 'PASS'
    assert payload['reports'][1]['report']['health']['overall_status'] == 'WARN'


def test_health_bundle_report_payload_detaches_nested_details() -> None:
    bundle = create_health_provider_bundle(
        [HealthReportProvider('application', lambda: _summary(HealthStatus.PASS, {'nested': {'value': 1}}))]
    )

    payload = health_bundle_report_payload(bundle)
    payload['reports'][0]['report']['health']['results'][0]['details']['nested']['value'] = 99

    source_summary = bundle.providers[0].collect()
    assert source_summary.results[0].details['nested']['value'] == 1


def test_health_bundle_report_payload_rejects_invalid_bundle() -> None:
    with pytest.raises(TypeError):
        health_bundle_report_payload(object())
