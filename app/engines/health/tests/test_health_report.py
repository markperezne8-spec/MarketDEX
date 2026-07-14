import pytest

from app.engines.health import (
    HealthResult,
    HealthStatus,
    health_report_payload,
    summarize_health_results,
)


def _result(
    name: str,
    status: HealthStatus,
    details: dict | None = None,
    remediation: str | None = None,
) -> HealthResult:
    return HealthResult(
        name,
        status,
        f'{name} summary',
        '2026-07-14T23:40:00Z',
        details or {},
        remediation=remediation,
    )


def test_health_report_payload_combines_snapshot_and_findings() -> None:
    summary = summarize_health_results(
        [
            _result('database', HealthStatus.PASS, {'latency_ms': 8}),
            _result('market_data', HealthStatus.WARN, remediation='Refresh credentials'),
        ]
    )

    report = health_report_payload(summary)

    assert report['health']['overall_status'] == 'WARN'
    assert report['health']['counts']['PASS'] == 1
    assert report['findings'] == [
        {
            'check_name': 'market_data',
            'status': 'WARN',
            'summary': 'market_data summary',
            'remediation': 'Refresh credentials',
        }
    ]


def test_health_report_payload_uses_deterministic_finding_order() -> None:
    summary = summarize_health_results(
        [
            _result('z_warn', HealthStatus.WARN),
            _result('b_fail', HealthStatus.FAIL),
            _result('a_fail', HealthStatus.FAIL),
            _result('unknown', HealthStatus.UNKNOWN),
        ]
    )

    report = health_report_payload(summary)

    assert [(finding['status'], finding['check_name']) for finding in report['findings']] == [
        ('FAIL', 'a_fail'),
        ('FAIL', 'b_fail'),
        ('WARN', 'z_warn'),
        ('UNKNOWN', 'unknown'),
    ]


def test_health_report_payload_for_pass_only_summary_has_no_findings() -> None:
    summary = summarize_health_results([_result('database', HealthStatus.PASS)])

    report = health_report_payload(summary)

    assert report['health']['overall_status'] == 'PASS'
    assert report['findings'] == []


def test_health_report_payload_detaches_snapshot_details() -> None:
    summary = summarize_health_results([_result('database', HealthStatus.PASS, {'nested': {'value': 1}})])

    report = health_report_payload(summary)
    report['health']['results'][0]['details']['nested']['value'] = 99

    assert summary.results[0].details['nested']['value'] == 1


def test_health_report_payload_rejects_invalid_summary() -> None:
    with pytest.raises(TypeError):
        health_report_payload(object())
