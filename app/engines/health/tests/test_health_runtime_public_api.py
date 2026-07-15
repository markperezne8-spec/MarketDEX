from app.engines import health


def test_runtime_composition_public_api_contract() -> None:
    runtime_exports = {
        'HealthRuntimeComposition',
        'build_runtime_health_report',
        'runtime_health_report_lines',
        'runtime_health_summary',
    }

    assert runtime_exports <= set(health.__all__)
    for export_name in runtime_exports:
        assert getattr(health, export_name) is not None
