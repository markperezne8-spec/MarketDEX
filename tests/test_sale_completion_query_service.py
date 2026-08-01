from datetime import datetime, timezone

import pytest

from core.sale_completion import (
    SaleCompletionCompleteness,
    SaleCompletionConflict,
    SaleCompletionCoverage,
    SaleCompletionUnavailable,
)
from core.sale_completion_repository import (
    SaleCompletionRepositoryDiagnostic,
    SaleCompletionRepositoryRead,
)
from services.sale_completion_query_service import SaleCompletionQueryService


AS_OF = datetime(2026, 7, 31, tzinfo=timezone.utc)


class RecordingRepository:
    def __init__(self, read: SaleCompletionRepositoryRead) -> None:
        self.read = read
        self.queries = []

    def query_sale_completion(self, query):
        self.queries.append(query)
        return self.read


def _coverage(completeness: SaleCompletionCompleteness) -> SaleCompletionCoverage:
    return SaleCompletionCoverage(
        requested_inventory_ids=("inventory-1",),
        requested_sale_ids=(),
        source_systems=("sales",),
        as_of=AS_OF,
        evidence_count=0,
        completeness=completeness,
    )


def test_service_constructs_query_and_uses_injected_repository() -> None:
    expected = SaleCompletionRepositoryRead(
        result=SaleCompletionUnavailable(
            status="unavailable",
            reason_code="coverage_unavailable",
            coverage=_coverage(SaleCompletionCompleteness.UNAVAILABLE),
        )
    )
    repository = RecordingRepository(expected)
    service = SaleCompletionQueryService(repository)

    actual = service.query(inventory_ids=("inventory-1",), as_of=AS_OF)

    assert actual is expected
    assert repository.queries[0].inventory_ids == ("inventory-1",)
    assert repository.queries[0].sale_ids == ()
    assert repository.queries[0].as_of is AS_OF


def test_service_preserves_unavailable_result_without_coercion() -> None:
    expected = SaleCompletionRepositoryRead(
        result=SaleCompletionUnavailable(
            status="unavailable",
            reason_code="source_read_failed",
            coverage=_coverage(SaleCompletionCompleteness.UNAVAILABLE),
        )
    )
    service = SaleCompletionQueryService(RecordingRepository(expected))

    actual = service.query(inventory_ids=("inventory-1",), as_of=AS_OF)

    assert actual is expected
    assert actual.result.reason_code == "source_read_failed"


def test_service_preserves_conflict_and_diagnostic_identity() -> None:
    diagnostic = SaleCompletionRepositoryDiagnostic(conflicts=())
    expected = SaleCompletionRepositoryRead(
        result=SaleCompletionConflict(
            status="conflict",
            reason_code="evidence_validation_conflict",
            coverage=_coverage(SaleCompletionCompleteness.CONFLICTING),
        ),
        diagnostic=diagnostic,
    )
    service = SaleCompletionQueryService(RecordingRepository(expected))

    actual = service.query(inventory_ids=("inventory-1",), as_of=AS_OF)

    assert actual is expected
    assert actual.diagnostic is diagnostic
    assert actual.result.reason_code == "evidence_validation_conflict"


def test_service_uses_existing_query_validation() -> None:
    repository = RecordingRepository(
        SaleCompletionRepositoryRead(
            result=SaleCompletionUnavailable(
                status="unavailable",
                reason_code="unused",
                coverage=_coverage(SaleCompletionCompleteness.UNAVAILABLE),
            )
        )
    )
    service = SaleCompletionQueryService(repository)

    with pytest.raises(ValueError, match="at least one inventory_id or sale_id is required"):
        service.query(as_of=AS_OF)

    assert repository.queries == []
