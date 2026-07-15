import pytest

from app.engines.health import (
    HealthReportProvider,
    HealthResult,
    HealthRuntimeComposition,
    HealthStatus,
    build_runtime_health_report,
    create_health_provider_bundle,
    runtime_health_report_lines,
    runtime_health_summary,
    summarize_health_results,
)


def _summary(status: HealthStatus = HealthStatus.PASS):
    return summarize_health_results(
        [HealthResult('database', status, 'database summary', '2026-07-15T00:45:00Z')]
    )


def _bundle():
    return create_health_provider_bundle(
        [
            HealthReportProvider('application', lambda: _summary(HealthStatus.PASS)),
            HealthReportProvider('database', lambda: _summary(HealthStatus.WARN)),
        ]
    )


def test_health_runtime_composition_is_immutable() -> None:
    composition = HealthRuntimeComposition('MarketDEX', _bundle())

    with pytest.raises(AttributeError):
        composition.runtime_name = 'Other'


def test_build_runtime_health_report_includes_runtime_and_health_payload() -> None:
    composition = HealthRuntimeComposition('MarketDEX', _bundle())

    report = build_runtime_health_report(composition)

    assert report['runtime'] == 'MarketDEX'
    assert report['health']['summary']['overall_status'] == 'WARN'
    assert [entry['provider'] for entry in report['health']['reports']] == ['application', 'database']


def test_runtime_health_summary_includes_runtime_and_bundle_summary() -> None:
    composition = HealthRuntimeComposition('MarketDEX', _bundle())

    summary = runtime_health_summary(composition)

    assert summary['runtime'] == 'MarketDEX'
    assert summary['health']['overall_status'] == 'WARN'
    assert [provider['name'] for provider in summary['health']['providers']] == ['application', 'database']


def test_runtime_health_report_lines_include_runtime_and_preserve_provider_order() -> None:
    composition = HealthRuntimeComposition('MarketDEX', _bundle())

    assert runtime_health_report_lines(composition) == (
        'runtime=MarketDEX',
        'overall=WARN',
        'providers=2',
        'provider=application:PASS:findings=0',
        'provider=database:WARN:findings=1',
    )


def test_health_runtime_composition_rejects_blank_runtime_name() -> None:
    with pytest.raises(ValueError):
        HealthRuntimeComposition('', _bundle())


def test_health_runtime_composition_rejects_invalid_bundle() -> None:
    with pytest.raises(TypeError):
        HealthRuntimeComposition('MarketDEX', object())


def test_build_runtime_health_report_rejects_invalid_composition() -> None:
    with pytest.raises(TypeError):
        build_runtime_health_report(object())


def test_runtime_health_summary_rejects_invalid_composition() -> None:
    with pytest.raises(TypeError):
        runtime_health_summary(object())


def test_runtime_health_report_lines_rejects_invalid_composition() -> None:
    with pytest.raises(TypeError):
        runtime_health_report_lines(object())
