import pytest

from app.engines.health import (
    HealthProviderBundle,
    HealthReportProvider,
    HealthResult,
    HealthStatus,
    build_health_reports,
    create_health_provider_bundle,
    summarize_health_results,
)


def _summary(status: HealthStatus = HealthStatus.PASS):
    return summarize_health_results(
        [HealthResult('database', status, 'database summary', '2026-07-15T00:15:00Z')]
    )


def test_create_health_provider_bundle_preserves_provider_order() -> None:
    first = HealthReportProvider('application', lambda: _summary())
    second = HealthReportProvider('database', lambda: _summary(HealthStatus.WARN))

    bundle = create_health_provider_bundle([first, second])

    assert bundle.providers == (first, second)


def test_build_health_reports_preserves_provider_order_and_names() -> None:
    bundle = create_health_provider_bundle(
        [
            HealthReportProvider('application', lambda: _summary()),
            HealthReportProvider('database', lambda: _summary(HealthStatus.WARN)),
        ]
    )

    reports = build_health_reports(bundle)

    assert [entry['provider'] for entry in reports] == ['application', 'database']
    assert reports[0]['report']['health']['overall_status'] == 'PASS'
    assert reports[1]['report']['health']['overall_status'] == 'WARN'


def test_health_provider_bundle_is_immutable() -> None:
    bundle = create_health_provider_bundle([HealthReportProvider('application', lambda: _summary())])

    with pytest.raises(AttributeError):
        bundle.providers = ()


def test_health_provider_bundle_rejects_duplicate_provider_names() -> None:
    provider = HealthReportProvider('application', lambda: _summary())

    with pytest.raises(ValueError):
        create_health_provider_bundle([provider, provider])


def test_health_provider_bundle_rejects_invalid_provider_item() -> None:
    with pytest.raises(TypeError):
        create_health_provider_bundle([object()])


def test_build_health_reports_rejects_invalid_bundle() -> None:
    with pytest.raises(TypeError):
        build_health_reports(object())
