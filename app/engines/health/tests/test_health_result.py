import pytest

from app.engines.health import HealthResult, HealthStatus


def test_health_result_detaches_details() -> None:
    details = {'latency_ms': 12}
    result = HealthResult('database', HealthStatus.PASS, 'Database ready', '2026-07-14T23:00:00Z', details)
    details['latency_ms'] = 99

    assert result.details['latency_ms'] == 12
    with pytest.raises(TypeError):
        result.details['latency_ms'] = 20


def test_health_result_rejects_invalid_identity() -> None:
    with pytest.raises(ValueError):
        HealthResult('', HealthStatus.FAIL, 'Failed', '2026-07-14T23:00:00Z')


def test_health_result_rejects_invalid_status() -> None:
    with pytest.raises(TypeError):
        HealthResult('database', 'PASS', 'Ready', '2026-07-14T23:00:00Z')


def test_health_result_rejects_blank_remediation() -> None:
    with pytest.raises(ValueError):
        HealthResult('database', HealthStatus.WARN, 'Needs review', '2026-07-14T23:00:00Z', remediation=' ')
