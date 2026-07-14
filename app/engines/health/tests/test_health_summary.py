import pytest

from app.engines.health import HealthResult, HealthStatus, summarize_health_results


def _result(name: str, status: HealthStatus) -> HealthResult:
    return HealthResult(name, status, f'{name} summary', '2026-07-14T23:15:00Z')


def test_summarize_health_results_preserves_order_and_counts() -> None:
    first = _result('database', HealthStatus.PASS)
    second = _result('market_data', HealthStatus.WARN)
    third = _result('brokerage', HealthStatus.UNKNOWN)

    summary = summarize_health_results([first, second, third])

    assert summary.results == (first, second, third)
    assert summary.counts[HealthStatus.PASS] == 1
    assert summary.counts[HealthStatus.WARN] == 1
    assert summary.counts[HealthStatus.UNKNOWN] == 1
    assert summary.counts[HealthStatus.FAIL] == 0


def test_summarize_health_results_uses_highest_status_precedence() -> None:
    summary = summarize_health_results(
        [
            _result('market_data', HealthStatus.WARN),
            _result('brokerage', HealthStatus.FAIL),
            _result('database', HealthStatus.PASS),
        ]
    )

    assert summary.overall_status is HealthStatus.FAIL


def test_summarize_health_results_empty_input_is_unknown() -> None:
    summary = summarize_health_results([])

    assert summary.overall_status is HealthStatus.UNKNOWN
    assert summary.results == ()
    assert all(count == 0 for count in summary.counts.values())


def test_health_summary_is_immutable() -> None:
    summary = summarize_health_results([_result('database', HealthStatus.PASS)])

    with pytest.raises(AttributeError):
        summary.overall_status = HealthStatus.FAIL
    with pytest.raises(TypeError):
        summary.counts[HealthStatus.FAIL] = 1


def test_summarize_health_results_rejects_invalid_items() -> None:
    with pytest.raises(TypeError):
        summarize_health_results([object()])
