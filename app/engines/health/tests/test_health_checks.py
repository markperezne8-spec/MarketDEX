import pytest

from app.engines.health import HealthCheck, HealthResult, HealthStatus, run_health_checks


def _result(name: str, status: HealthStatus = HealthStatus.PASS) -> HealthResult:
    return HealthResult(name, status, f'{name} summary', '2026-07-14T23:20:00Z')


def test_run_health_checks_preserves_order_and_aggregates_summary() -> None:
    calls: list[str] = []
    checks = (
        HealthCheck('database', lambda: calls.append('database') or _result('database')),
        HealthCheck('market_data', lambda: calls.append('market_data') or _result('market_data', HealthStatus.WARN)),
    )

    summary = run_health_checks(checks)

    assert calls == ['database', 'market_data']
    assert [result.check_name for result in summary.results] == ['database', 'market_data']
    assert summary.overall_status is HealthStatus.WARN
    assert summary.counts[HealthStatus.PASS] == 1
    assert summary.counts[HealthStatus.WARN] == 1


def test_health_check_contract_is_immutable() -> None:
    check = HealthCheck('database', lambda: _result('database'))

    with pytest.raises(AttributeError):
        check.name = 'market_data'


def test_health_check_rejects_invalid_name() -> None:
    with pytest.raises(ValueError):
        HealthCheck('', lambda: _result('database'))


def test_health_check_rejects_non_callable_runner() -> None:
    with pytest.raises(TypeError):
        HealthCheck('database', object())


def test_run_health_checks_rejects_invalid_check_item() -> None:
    with pytest.raises(TypeError):
        run_health_checks([object()])


def test_run_health_checks_rejects_invalid_result() -> None:
    with pytest.raises(TypeError):
        run_health_checks([HealthCheck('database', lambda: object())])


def test_run_health_checks_requires_matching_result_name() -> None:
    with pytest.raises(ValueError):
        run_health_checks([HealthCheck('database', lambda: _result('market_data'))])
