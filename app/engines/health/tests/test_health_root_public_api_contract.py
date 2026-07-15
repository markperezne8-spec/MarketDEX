from app.engines import health
from app.engines.health.application_lines import health_application_lines
from app.engines.health.application_payload import health_application_payload
from app.engines.health.root_lines import health_root_lines
from app.engines.health.root_payload import health_root_payload
from app.engines.health.root_registration import HealthRootRegistration
from app.engines.health.root_registry import RegisteredHealthRoot, register_health_root


def test_health_root_public_api_exports_only_approved_symbols() -> None:
    expected = {
        'HealthRootRegistration': HealthRootRegistration,
        'RegisteredHealthRoot': RegisteredHealthRoot,
        'register_health_root': register_health_root,
        'health_root_payload': health_root_payload,
        'health_root_lines': health_root_lines,
    }

    assert set(expected) <= set(health.__all__)
    for name, implementation in expected.items():
        assert getattr(health, name) is implementation


def test_health_root_public_api_preserves_existing_application_authority() -> None:
    assert health.health_application_payload is health_application_payload
    assert health.health_application_lines is health_application_lines
