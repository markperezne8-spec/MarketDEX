import app.engines.health as health


EXPECTED_HEALTH_EXPORTS = [
    'HealthStatus',
    'HealthResult',
    'HealthSummary',
    'HealthCheck',
    'HealthFinding',
    'validate_health_result',
    'summarize_health_results',
    'health_summary_snapshot',
    'health_findings',
    'health_report_payload',
    'health_report_lines',
    'run_health_checks',
]


def test_health_public_exports_are_deterministic() -> None:
    assert health.__all__ == EXPECTED_HEALTH_EXPORTS


def test_health_public_exports_are_unique() -> None:
    assert len(health.__all__) == len(set(health.__all__))


def test_health_public_exports_resolve() -> None:
    for export_name in EXPECTED_HEALTH_EXPORTS:
        assert getattr(health, export_name) is not None
