import pytest

from app.engines.health import (
    HealthResult,
    HealthStatus,
    health_report_lines,
    summarize_health_results,
)


def _result(name: str, status: HealthStatus) -> HealthResult:
    return HealthResult(name, status, f'{name} summary', '2026-07-14T23:55:00Z')


def test_health_report_lines_for_pass_only_summary() -> None:
    summary = summarize_health_results([_result('database', HealthStatus.PASS)])

    lines = health_report_lines(summary)

    assert lines == (
        'overall=PASS',
        'counts=FAIL:0,PASS:1,UNKNOWN:0,WARN:0',
        'findings=none',
    )


def test_health_report_lines_include_ordered_findings() -> None:
    summary = summarize_health_results(
        [
            _result('z_warn', HealthStatus.WARN),
            _result('b_fail', HealthStatus.FAIL),
            _result('a_fail', HealthStatus.FAIL),
            _result('unknown', HealthStatus.UNKNOWN),
        ]
    )

    lines = health_report_lines(summary)

    assert lines == (
        'overall=FAIL',
        'counts=FAIL:2,PASS:0,UNKNOWN:1,WARN:1',
        'findings=4',
        'finding=FAIL:a_fail:a_fail summary',
        'finding=FAIL:b_fail:b_fail summary',
        'finding=WARN:z_warn:z_warn summary',
        'finding=UNKNOWN:unknown:unknown summary',
    )


def test_health_report_lines_empty_summary_is_unknown() -> None:
    summary = summarize_health_results([])

    lines = health_report_lines(summary)

    assert lines == (
        'overall=UNKNOWN',
        'counts=FAIL:0,PASS:0,UNKNOWN:0,WARN:0',
        'findings=none',
    )


def test_health_report_lines_rejects_invalid_summary() -> None:
    with pytest.raises(TypeError):
        health_report_lines(object())
