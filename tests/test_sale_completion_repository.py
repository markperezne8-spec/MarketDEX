from datetime import datetime, timedelta, timezone

from core.sale_completion import (
    SaleCompletionAvailable,
    SaleCompletionConflict,
    SaleCompletionEvidence,
    SaleCompletionLifecycleState,
    SaleCompletionQuery,
    SaleCompletionUnavailable,
)
from core.sale_completion_repository import (
    SaleCompletionRepository,
    SaleCompletionRepositoryRead,
    build_sale_completion_repository_read,
)
from core.sale_completion_validation import SaleCompletionEvidenceConflictCode


NOW = datetime(2026, 7, 26, 17, 0, tzinfo=timezone.utc)
EARLIER = NOW - timedelta(hours=1)


def completed(evidence_id: str, *, sale_id: str = "sale-1") -> SaleCompletionEvidence:
    return SaleCompletionEvidence(
        sale_completion_evidence_id=evidence_id,
        sale_id=sale_id,
        inventory_id="inventory-1",
        lifecycle_state=SaleCompletionLifecycleState.COMPLETED,
        source_system="canonical-sales",
        recorded_at=NOW,
        completed_unit_quantity=1,
        completed_at=EARLIER,
    )


def query() -> SaleCompletionQuery:
    return SaleCompletionQuery(inventory_ids=("inventory-1",), sale_ids=("sale-1",), as_of=NOW)


def test_complete_valid_evidence_returns_available_in_canonical_order():
    later = completed("evidence-2")
    earlier = SaleCompletionEvidence(
        sale_completion_evidence_id="evidence-1",
        sale_id="sale-2",
        inventory_id="inventory-2",
        lifecycle_state=SaleCompletionLifecycleState.PENDING,
        source_system="canonical-sales",
        recorded_at=EARLIER - timedelta(hours=1),
    )
    read = build_sale_completion_repository_read(
        query=query(), evidence=(later, earlier), source_systems=("canonical-sales", "canonical-sales"), coverage_complete=True
    )
    assert isinstance(read.result, SaleCompletionAvailable)
    assert read.result.evidence == (earlier, later)
    assert read.result.coverage.source_systems == ("canonical-sales",)
    assert read.diagnostic is None


def test_unknown_coverage_is_unavailable_even_for_empty_evidence():
    read = build_sale_completion_repository_read(
        query=query(), evidence=(), source_systems=(), coverage_complete=False
    )
    assert isinstance(read.result, SaleCompletionUnavailable)
    assert read.result.reason_code == "coverage_unavailable"
    assert read.diagnostic is None


def test_validation_conflict_preserves_codes_and_evidence_ids():
    duplicate = completed("duplicate")
    read = build_sale_completion_repository_read(
        query=query(), evidence=(duplicate, duplicate), source_systems=("canonical-sales",), coverage_complete=True
    )
    assert isinstance(read.result, SaleCompletionConflict)
    assert read.result.reason_code == "evidence_validation_conflict"
    assert read.diagnostic is not None
    assert read.diagnostic.evidence_ids == ("duplicate",)
    assert {conflict.code for conflict in read.diagnostic.conflicts} >= {
        SaleCompletionEvidenceConflictCode.DUPLICATE_EVIDENCE_IDENTITY
    }


def test_in_memory_fake_satisfies_runtime_protocol():
    class FakeRepository:
        def query_sale_completion(self, requested: SaleCompletionQuery) -> SaleCompletionRepositoryRead:
            return build_sale_completion_repository_read(
                query=requested, evidence=(), source_systems=("fake",), coverage_complete=True
            )
    assert isinstance(FakeRepository(), SaleCompletionRepository)
    assert isinstance(FakeRepository().query_sale_completion(query()).result, SaleCompletionAvailable)
