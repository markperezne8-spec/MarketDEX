import app.engines.health as health


def test_health_application_contracts_are_publicly_exported() -> None:
    expected = {
        'HealthApplicationRequest',
        'HealthApplicationBoundary',
        'adapt_health_application_request',
        'health_application_payload',
        'health_application_lines',
    }

    assert expected.issubset(set(health.__all__))
    for name in expected:
        assert hasattr(health, name)
