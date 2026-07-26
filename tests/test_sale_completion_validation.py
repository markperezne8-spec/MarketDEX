from datetime import datetime, timedelta, timezone

from core.sale_completion import SaleCompletionEvidence, SaleCompletionLifecycleState
from core.sale_completion_validation import (
    SaleCompletionEvidenceConflictCode,
    SaleCompletionEvidenceSetConflict,
    SaleCompletionEvidenceSetValid,
    validate_sale_completion_evidence_set,
)


NOW = datetime(2026, 7, 26, 16, 0, tzinfo=timezone.utc)
EARLIER = NOW - timedelta(hours=2)


def evidence(
    evidence_id: str,
    state: SaleCompletionLifecycleState,
    *,
    parent: str | None = None,
    sale_id: str = "sale-1",
    inventory_id: str = "inventory-1",
    recorded_at: datetime = NOW,
    completed_at: datetime | None = None,
    quantity: int | None = None,
) -> SaleCompletionEvidence:
    return SaleCompletionEvidence(
        sale_completion_evidence_id=evidence_id,
        sale_id=sale_id,
        inventory_id=inventory_id,
        lifecycle_state=state,
        source_system="canonical-sales",
        recorded_at=recorded_at,
        lineage_parent_evidence_id=parent,
        completed_unit_quantity=quantity,
        completed_at=completed_at,
    )


def codes(result: SaleCompletionEvidenceSetConflict) -> set[SaleCompletionEvidenceConflictCode]:
    return {conflict.code for conflict in result.conflicts}


def test_valid_set_returns_canonical_order_and_as_of():
    pending = evidence("evidence-1", SaleCompletionLifecycleState.PENDING, recorded_at=EARLIER)
    completed = evidence(
        "evidence-2",
        SaleCompletionLifecycleState.COMPLETED,
        parent="evidence-1",
        recorded_at=NOW,
        completed_at=EARLIER + timedelta(hours=1),
        quantity=2,
    )

    result = validate_sale_completion_evidence_set((completed, pending), as_of=NOW)

    assert isinstance(result, SaleCompletionEvidenceSetValid)
    assert result.evidence == (pending, completed)
    assert result.as_of == NOW


def test_duplicate_identity_and_required_ordering_fail_closed():
    first = evidence("duplicate", SaleCompletionLifecycleState.PENDING, recorded_at=EARLIER)
    second = evidence("duplicate", SaleCompletionLifecycleState.CANCELLED, recorded_at=NOW)

    result = validate_sale_completion_evidence_set(
        (second, first),
        as_of=NOW,
        require_canonical_input_order=True,
    )

    assert isinstance(result, SaleCompletionEvidenceSetConflict)
    assert SaleCompletionEvidenceConflictCode.DUPLICATE_EVIDENCE_IDENTITY in codes(result)
    assert SaleCompletionEvidenceConflictCode.NON_CANONICAL_ORDERING in codes(result)


def test_missing_parent_and_linkage_conflicts_are_typed():
    missing = evidence(
        "evidence-2",
        SaleCompletionLifecycleState.REFUNDED,
        parent="missing-parent",
    )
    parent = evidence("evidence-3", SaleCompletionLifecycleState.COMPLETED, completed_at=EARLIER, quantity=1)
    linked = evidence(
        "evidence-4",
        SaleCompletionLifecycleState.REFUNDED,
        parent="evidence-3",
        sale_id="sale-2",
        inventory_id="inventory-2",
    )

    result = validate_sale_completion_evidence_set((missing, parent, linked), as_of=NOW)

    assert isinstance(result, SaleCompletionEvidenceSetConflict)
    assert SaleCompletionEvidenceConflictCode.MISSING_LINEAGE_PARENT in codes(result)
    assert SaleCompletionEvidenceConflictCode.CONFLICTING_SALE_LINKAGE in codes(result)
    assert SaleCompletionEvidenceConflictCode.CONFLICTING_INVENTORY_LINKAGE in codes(result)


def test_cycle_and_branch_are_detected_deterministically():
    first = evidence("evidence-1", SaleCompletionLifecycleState.REFUNDED, parent="evidence-2")
    second = evidence("evidence-2", SaleCompletionLifecycleState.SUPERSEDED, parent="evidence-1")
    root = evidence("root", SaleCompletionLifecycleState.COMPLETED, completed_at=EARLIER, quantity=1)
    branch_a = evidence("branch-a", SaleCompletionLifecycleState.REFUNDED, parent="root")
    branch_b = evidence("branch-b", SaleCompletionLifecycleState.REVERSED, parent="root")

    result = validate_sale_completion_evidence_set((first, second, root, branch_a, branch_b), as_of=NOW)

    assert isinstance(result, SaleCompletionEvidenceSetConflict)
    assert SaleCompletionEvidenceConflictCode.LINEAGE_CYCLE in codes(result)
    assert SaleCompletionEvidenceConflictCode.AMBIGUOUS_LINEAGE_BRANCH in codes(result)


def test_timestamp_as_of_transition_and_terminal_conflicts_are_detected():
    future = evidence(
        "future",
        SaleCompletionLifecycleState.COMPLETED,
        recorded_at=NOW + timedelta(hours=2),
        completed_at=NOW + timedelta(hours=1),
        quantity=1,
    )
    invalid_time = evidence(
        "invalid-time",
        SaleCompletionLifecycleState.COMPLETED,
        recorded_at=EARLIER,
        completed_at=NOW,
        quantity=1,
        sale_id="sale-2",
    )
    cancelled = evidence("cancelled", SaleCompletionLifecycleState.CANCELLED, sale_id="sale-3")
    refunded = evidence(
        "refunded",
        SaleCompletionLifecycleState.REFUNDED,
        parent="cancelled",
        sale_id="sale-3",
    )
    terminal_a = evidence("terminal-a", SaleCompletionLifecycleState.PENDING, sale_id="sale-4")
    terminal_b = evidence("terminal-b", SaleCompletionLifecycleState.CANCELLED, sale_id="sale-4")

    result = validate_sale_completion_evidence_set(
        (future, invalid_time, cancelled, refunded, terminal_a, terminal_b),
        as_of=NOW,
    )

    assert isinstance(result, SaleCompletionEvidenceSetConflict)
    assert SaleCompletionEvidenceConflictCode.EVIDENCE_AFTER_AS_OF in codes(result)
    assert SaleCompletionEvidenceConflictCode.TIMESTAMP_CONFLICT in codes(result)
    assert SaleCompletionEvidenceConflictCode.UNSUPPORTED_LIFECYCLE_TRANSITION in codes(result)
    assert SaleCompletionEvidenceConflictCode.MULTIPLE_ACTIVE_TERMINAL_EVIDENCE in codes(result)
