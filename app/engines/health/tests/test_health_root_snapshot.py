from dataclasses import FrozenInstanceError

import pytest

from app.engines.health.application_adapter import HealthApplicationBoundary
from app.engines.health.bundle import create_health_provider_bundle
from app.engines.health.provider import HealthReportProvider
from app.engines.health.result import HealthResult, HealthStatus
from app.engines.health.root_registration import HealthRootRegistration
from app.engines.health.root_registry import register_health_root
from app.engines.health.root_snapshot import HealthRootSnapshot, snapshot_health_root
from app.engines.health.runtime import HealthRuntimeComposition
from app.engines.health.summary import summarize_health_results


def _summary(status: HealthStatus):
    return summarize_health_results(
        [HealthResult('database', status, 'database summary', '2026-07-15T00:45:00Z')]
    )


def _registered_root():
    bundle = create_health_provider_bundle(
        [
            HealthReportProvider('application', lambda: _summary(HealthStatus.PASS)),
            HealthReportProvider('database', lambda: _summary(HealthStatus.WARN)),
        ]
    )
    composition = HealthRuntimeComposition('MarketDEX', bundle)
    boundary = HealthApplicationBoundary('desktop', composition)
    return register_health_root(HealthRootRegistration('desktop-health', boundary))


def test_snapshot_health_root_is_deterministic_and_preserves_shape() -> None:
    snapshot = snapshot_health_root(_registered_root())

    assert snapshot == HealthRootSnapshot(
        registration_name='desktop-health',
        payload={
            'boundary': 'desktop',
            'runtime': {
                'runtime': 'MarketDEX',
                'health': {
                    'summary': {
                        'overall_status': 'WARN',
                        'provider_count': 2,
                        'providers': [
                            {'name': 'application', 'overall_status': 'PASS', 'finding_count': 0},
                            {'name': 'database', 'overall_status': 'WARN', 'finding_count': 1},
                        ],
                    },
                    'reports': [
                        {'provider': 'application', 'report': {'health': {'overall_status': 'PASS', 'counts': {'FAIL': 0, 'PASS': 1, 'UNKNOWN': 0, 'WARN': 0}, 'results': [{'check_name': 'database', 'status': 'PASS', 'summary': 'database summary', 'checked_at': '2026-07-15T00:45:00Z', 'details': {}, 'remediation': None}]}, 'findings': []}},
                        {'provider': 'database', 'report': {'health': {'overall_status': 'WARN', 'counts': {'FAIL': 0, 'PASS': 0, 'UNKNOWN': 0, 'WARN': 1}, 'results': [{'check_name': 'database', 'status': 'WARN', 'summary': 'database summary', 'checked_at': '2026-07-15T00:45:00Z', 'details': {}, 'remediation': None}]}, 'findings': [{'check_name': 'database', 'status': 'WARN', 'summary': 'database summary', 'remediation': None}]}}],
                },
            },
        },
    )


def test_snapshot_health_root_preserves_registration_and_order() -> None:
    registered_root = _registered_root()
    snapshot = snapshot_health_root(registered_root)

    assert snapshot.registration_name == registered_root.registration_name
    assert [
        report['provider'] for report in snapshot.payload['runtime']['health']['reports']
    ] == ['application', 'database']


def test_health_root_snapshot_is_immutable() -> None:
    snapshot = snapshot_health_root(_registered_root())

    with pytest.raises(FrozenInstanceError):
        snapshot.registration_name = 'other'


def test_snapshot_health_root_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match='registered_root must be a RegisteredHealthRoot'):
        snapshot_health_root(object())
