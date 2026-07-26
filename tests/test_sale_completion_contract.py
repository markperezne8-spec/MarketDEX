from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from core.sale_completion import (
    SaleCompletionAvailable,
    SaleCompletionCompleteness,
    SaleCompletionConflict,
    SaleCompletionCoverage,
    SaleCompletionEvidence,
    SaleCompletionLifecycleState,
    SaleCompletionQuery,
    SaleCompletionUnavailable,
)


NOW = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
EARLIER = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)


def completed_evidence(evidence_id: str = "evidence-1", completed_at: datetime = EARLIER):
    return SaleCompletionEvidence(
        sale_completion_evidence_id=evidence_id,
        sale_id="sale-1",
        inventory_id="inventory-1",
        lifecycle_state=SaleCompletionLifecycleState.COMPLETED,
        source_system="canonical-sales",
        recorded_at=NOW,
        completed_unit_quantity=1,
        completed_at=completed_at,
    )


def coverage(completeness: SaleCompletionCompleteness, evidence_count: int = 0):
    return SaleCompletionCoverage(
        requested_inventory_ids=("inventory-1",),
        requested_sale_ids=("sale-1",),
        source_systems=("canonical-sales",),
        as_of=NOW,
        evidence_count=evidence_count,
        completeness=completeness,
    )


def test_completed_evidence_is_immutable_and_has_canonical_ordering_key():
    evidence = completed_evidence()

    assert evidence.ordering_key == (
        EARLIER,
        NOW,
        "sale-1",
        "inventory-1",
        "evidence-1",
    )
    with pytest.raises(FrozenInstanceError):
        evidence.sale_id = "changed"


@pytest.mark.parametrize("quantity", [None, 0, -1, 1.5, True])
def test_completed_evidence_requires_positive_whole_unit_quantity(quantity):
    with pytest.raises(ValueError, match="positive whole-unit quantity"):
        SaleCompletionEvidence(
            sale_completion_evidence_id="evidence-1",
            sale_id="sale-1",
            inventory_id="inventory-1",
            lifecycle_state=SaleCompletionLifecycleState.COMPLETED,
            source_system="canonical-sales",
            recorded_at=NOW,
            completed_unit_quantity=quantity,
            completed_at=EARLIER,
        )


def test_non_completed_evidence_cannot_carry_completion_fields():
    with pytest.raises(ValueError, match="only completed evidence"):
        SaleCompletionEvidence(
            sale_completion_evidence_id="evidence-1",
            sale_id="sale-1",
            inventory_id="inventory-1",
            lifecycle_state=SaleCompletionLifecycleState.PENDING,
            source_system="canonical-sales",
            recorded_at=NOW,
            completed_unit_quantity=1,
            completed_at=EARLIER,
        )


@pytest.mark.parametrize(
    "state",
    [
        SaleCompletionLifecycleState.REFUNDED,
        SaleCompletionLifecycleState.REVERSED,
        SaleCompletionLifecycleState.SUPERSEDED,
    ],
)
def test_correction_states_require_lineage(state):
    with pytest.raises(ValueError, match="requires lineage_parent_evidence_id"):
        SaleCompletionEvidence(
            sale_completion_evidence_id="evidence-2",
            sale_id="sale-1",
            inventory_id="inventory-1",
            lifecycle_state=state,
            source_system="canonical-sales",
            recorded_at=NOW,
        )


def test_query_requires_identity_scope_and_valid_time_range():
    with pytest.raises(ValueError, match="at least one"):
        SaleCompletionQuery(inventory_ids=(), sale_ids=(), as_of=NOW)

    with pytest.raises(ValueError, match="earlier than"):
        SaleCompletionQuery(
            inventory_ids=("inventory-1",),
            sale_ids=(),
            as_of=NOW,
            completed_from=NOW,
            completed_until=EARLIER,
        )


def test_available_result_requires_complete_matching_ordered_evidence():
    evidence = completed_evidence()
    result = SaleCompletionAvailable(
        status="available",
        evidence=(evidence,),
        coverage=coverage(SaleCompletionCompleteness.COMPLETE, evidence_count=1),
    )

    assert result.evidence == (evidence,)

    later = completed_evidence("evidence-2", NOW)
    with pytest.raises(ValueError, match="canonical ordering"):
        SaleCompletionAvailable(
            status="available",
            evidence=(later, evidence),
            coverage=coverage(SaleCompletionCompleteness.COMPLETE, evidence_count=2),
        )


def test_unavailable_and_conflict_results_require_matching_coverage():
    unavailable = SaleCompletionUnavailable(
        status="unavailable",
        reason_code="source_not_available",
        coverage=coverage(SaleCompletionCompleteness.UNAVAILABLE),
    )
    conflict = SaleCompletionConflict(
        status="conflict",
        reason_code="duplicate_evidence",
        coverage=coverage(SaleCompletionCompleteness.CONFLICTING),
    )

    assert unavailable.reason_code == "source_not_available"
    assert conflict.reason_code == "duplicate_evidence"

    with pytest.raises(ValueError, match="unavailable coverage"):
        SaleCompletionUnavailable(
            status="unavailable",
            reason_code="source_not_available",
            coverage=coverage(SaleCompletionCompleteness.COMPLETE),
        )


def test_all_contract_datetimes_must_be_timezone_aware():
    naive = datetime(2026, 7, 26, 12, 0)

    with pytest.raises(ValueError, match="timezone-aware"):
        completed_evidence(completed_at=naive)

    with pytest.raises(ValueError, match="timezone-aware"):
        SaleCompletionQuery(
            inventory_ids=("inventory-1",),
            sale_ids=(),
            as_of=naive,
        )
