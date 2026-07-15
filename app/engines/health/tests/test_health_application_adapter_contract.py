from app.engines.health.application_adapter import (
    HealthApplicationBoundary,
    adapt_health_application_request,
)


def test_health_application_adapter_module_exports_are_stable() -> None:
    assert HealthApplicationBoundary.__name__ == 'HealthApplicationBoundary'
    assert adapt_health_application_request.__name__ == 'adapt_health_application_request'
