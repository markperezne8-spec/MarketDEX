from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone

import pytest

from core.inventory_acquisition_projection import (
    InventoryAcquisitionProjectionAvailable,
    InventoryAcquisitionProjectionConflict,
    InventoryAcquisitionProjectionCoverage,
    InventoryAcquisitionProjectionDiagnostic,
    InventoryAcquisitionProjectionRecord,
    InventoryAcquisitionProjectionRequest,
    InventoryAcquisitionProjectionState,
    InventoryAcquisitionProjectionUnavailable,
)


UTC = timezone.utc


def _request() -> InventoryAcquisitionProjectionRequest:
    return InventoryAcquisitionProjectionRequest(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 2, 1),
        as_of=datetime(2026, 1, 31, 23, 59, tzinfo=UTC),
    )


def _coverage(request: InventoryAcquisitionProjectionRequest) -> InventoryAcquisitionProjectionCoverage:
    return InventoryAcquisitionProjectionCoverage(
        period_start=request.period_start,
        period_end=request.period_end,
        as_of=request.as_of,
    )


def test_available_projection_orders_records_deterministically_and_preserves_exact_labels() -> None:
    request = _request()
    result = InventoryAcquisitionProjectionAvailable(
        request=request,
        coverage=_coverage(request),
        records=(
            InventoryAcquisitionProjectionRecord('b', 2, date(2026, 1, 5), 'Store'),
            InventoryAcquisitionProjectionRecord('a', 1, date(2026, 1, 5), 'store'),
            InventoryAcquisitionProjectionRecord('c', 3, date(2026, 1, 4), 'Other'),
        ),
        provenance=('inventory-acquisition-projection:test',),
    )

    assert tuple(record.inventory_id for record in result.records) == ('c', 'a', 'b')
    assert tuple(record.purchase_source_label for record in result.records) == ('Other', 'store', 'Store')
    assert result.state is InventoryAcquisitionProjectionState.AVAILABLE


def test_empty_complete_coverage_is_valid() -> None:
    request = _request()
    result = InventoryAcquisitionProjectionAvailable(
        request=request,
        coverage=_coverage(request),
        records=(),
        provenance=('inventory-acquisition-projection:empty',),
    )
    assert result.records == ()


@pytest.mark.parametrize('units', [0, -1, 1.5, True])
def test_record_rejects_invalid_acquired_units(units: object) -> None:
    with pytest.raises(ValueError):
        InventoryAcquisitionProjectionRecord('inv-1', units, date(2026, 1, 2), 'Source')  # type: ignore[arg-type]


def test_record_rejects_invalid_date_and_blank_label() -> None:
    with pytest.raises(TypeError):
        InventoryAcquisitionProjectionRecord('inv-1', 1, '2026-01-02', 'Source')  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        InventoryAcquisitionProjectionRecord('inv-1', 1, date(2026, 1, 2), '  ')


def test_request_requires_timezone_aware_as_of_and_valid_period() -> None:
    with pytest.raises(TypeError):
        InventoryAcquisitionProjectionRequest(date(2026, 1, 1), date(2026, 2, 1), datetime(2026, 1, 31))
    with pytest.raises(ValueError):
        InventoryAcquisitionProjectionRequest(date(2026, 2, 1), date(2026, 2, 1), datetime(2026, 2, 1, tzinfo=UTC))


def test_available_rejects_duplicate_identity_and_coverage_mismatch() -> None:
    request = _request()
    duplicate = InventoryAcquisitionProjectionRecord('inv-1', 1, date(2026, 1, 2), 'Source')
    with pytest.raises(ValueError, match='duplicate'):
        InventoryAcquisitionProjectionAvailable(
            request=request,
            coverage=_coverage(request),
            records=(duplicate, duplicate),
            provenance=('projection:test',),
        )

    mismatched = InventoryAcquisitionProjectionCoverage(
        date(2026, 1, 2), date(2026, 2, 1), request.as_of,
    )
    with pytest.raises(ValueError, match='coverage'):
        InventoryAcquisitionProjectionAvailable(
            request=request,
            coverage=mismatched,
            records=(),
            provenance=('projection:test',),
        )


def test_available_rejects_out_of_period_and_after_as_of_records() -> None:
    request = _request()
    with pytest.raises(ValueError, match='outside'):
        InventoryAcquisitionProjectionAvailable(
            request=request,
            coverage=_coverage(request),
            records=(InventoryAcquisitionProjectionRecord('inv-1', 1, date(2026, 2, 1), 'Source'),),
            provenance=('projection:test',),
        )

    limited_request = InventoryAcquisitionProjectionRequest(
        date(2026, 1, 1), date(2026, 2, 1), datetime(2026, 1, 10, tzinfo=UTC),
    )
    with pytest.raises(ValueError, match='as_of'):
        InventoryAcquisitionProjectionAvailable(
            request=limited_request,
            coverage=_coverage(limited_request),
            records=(InventoryAcquisitionProjectionRecord('inv-1', 1, date(2026, 1, 11), 'Source'),),
            provenance=('projection:test',),
        )


def test_unavailable_and_conflicting_outcomes_preserve_diagnostics() -> None:
    request = _request()
    unavailable = InventoryAcquisitionProjectionUnavailable(
        request,
        InventoryAcquisitionProjectionDiagnostic('purchase_source_missing', 'Purchase source is missing', ('inv-1',)),
    )
    conflict = InventoryAcquisitionProjectionConflict(
        request,
        InventoryAcquisitionProjectionDiagnostic('duplicate_canonical_inventory_identity', 'Duplicate identity', ('inv-1',)),
    )
    assert unavailable.state is InventoryAcquisitionProjectionState.UNAVAILABLE
    assert conflict.state is InventoryAcquisitionProjectionState.CONFLICTING
    assert unavailable.diagnostic.reason_code == 'purchase_source_missing'
    assert conflict.diagnostic.inventory_ids == ('inv-1',)


def test_contracts_are_immutable() -> None:
    request = _request()
    record = InventoryAcquisitionProjectionRecord('inv-1', 1, date(2026, 1, 2), 'Source')
    with pytest.raises(FrozenInstanceError):
        request.period_start = date(2025, 1, 1)  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        record.acquired_units = 2  # type: ignore[misc]


def test_contract_module_has_no_sqlite_or_repository_dependency() -> None:
    import core.inventory_acquisition_projection as module

    names = set(module.__dict__)
    assert 'sqlite3' not in names
    assert all('Repository' not in name for name in names)
