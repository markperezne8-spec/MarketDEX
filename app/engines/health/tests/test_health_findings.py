import pytest

from app.engines.health import (
    HealthFinding,
    HealthResult,
    HealthStatus,
    health_findings,
    summarize_health_results,
)


def _result(
    name: str,
    status: HealthStatus,
    remediation: str | None = None,
) -> HealthResult:
    return HealthResult(
        name,
        status,
        f'{name} summary',
        '2026-07-14T23:35:00Z',
        remediation=remediation,
    )


def test_health_findings_filters_passing_results() -> None:
    summary = summarize_health_results(
        [
            _result('database', HealthStatus.PASS),
            _result('market_data', HealthStatus.WARN),
        ]
    )

    findings = health_findings(summary)

    assert [finding.check_name for finding in findings] == ['market_data']


def test_health_findings_sorts_by_severity_then_name() -> None:
    summary = summarize_health_results(
        [
            _result('z_warn', HealthStatus.WARN),
            _result('b_fail', HealthStatus.FAIL),
            _result('a_fail', HealthStatus.FAIL),
            _result('unknown', HealthStatus.UNKNOWN),
        ]
    )

    findings = health_findings(summary)

    assert [(finding.status, finding.check_name) for finding in findings] == [
        (HealthStatus.FAIL, 'a_fail'),
        (HealthStatus.FAIL, 'b_fail'),
        (HealthStatus.WARN, 'z_warn'),
        (HealthStatus.UNKNOWN, 'unknown'),
    ]


def test_health_findings_preserves_remediation() -> None:
    summary = summarize_health_results(
        [_result('market_data', HealthStatus.WARN, remediation='Refresh market data credentials')]
    )

    findings = health_findings(summary)

    assert findings[0].remediation == 'Refresh market data credentials'


def test_health_finding_is_immutable() -> None:
    finding = HealthFinding('database', HealthStatus.FAIL, 'database summary')

    with pytest.raises(AttributeError):
        finding.summary = 'changed'


def test_health_finding_rejects_passing_status() -> None:
    with pytest.raises(ValueError):
        HealthFinding('database', HealthStatus.PASS, 'database summary')


def test_health_finding_rejects_blank_remediation() -> None:
    with pytest.raises(ValueError):
        HealthFinding('database', HealthStatus.WARN, 'database summary', remediation=' ')


def test_health_findings_rejects_invalid_summary() -> None:
    with pytest.raises(TypeError):
        health_findings(object())
