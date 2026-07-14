import pytest

from app.engines.health import (
    HealthResult,
    HealthStatus,
    health_summary_snapshot,
    summarize_health_results,
)


def _result(name: str, status: HealthStatus, details: dict | None = None) -> HealthResult:
    return HealthResult(
        name,
        status,
        f'{name} summary',
        '2026-07-14T23:25:00Z',
        details or {},
        remediation='Review configuration' if status is HealthStatus.WARN else None,
    )


def test_health_summary_snapshot_exports_json_safe_status_values() -> None:
    summary = summarize_health_results(
        [
            _result('database', HealthStatus.PASS, {'latency_ms': 12}),
            _result('market_data', HealthStatus.WARN, {'source': 'cache'}),
        ]
    )

    snapshot = health_summary_snapshot(summary)

    assert snapshot['overall_status'] == 'WARN'
    assert snapshot['counts'] == {'FAIL': 0, 'PASS': 1, 'UNKNOWN': 0, 'WARN': 1}
    assert [result['check_name'] for result in snapshot['results']] == ['database', 'market_data']
    assert snapshot['results'][0]['status'] == 'PASS'
    assert snapshot['results'][1]['remediation'] == 'Review configuration'


def test_health_summary_snapshot_detaches_nested_details() -> None:
    summary = summarize_health_results([_result('database', HealthStatus.PASS, {'nested': {'value': 1}})])

    snapshot = health_summary_snapshot(summary)
    snapshot['results'][0]['details']['nested']['value'] = 99

    assert summary.results[0].details['nested']['value'] == 1


def test_health_summary_snapshot_rejects_invalid_summary() -> None:
    with pytest.raises(TypeError):
        health_summary_snapshot(object())
