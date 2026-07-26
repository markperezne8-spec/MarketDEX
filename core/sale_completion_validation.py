from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal, TypeAlias

from core.sale_completion import SaleCompletionEvidence, SaleCompletionLifecycleState


class SaleCompletionEvidenceConflictCode(str, Enum):
    DUPLICATE_EVIDENCE_IDENTITY = "duplicate_evidence_identity"
    MISSING_LINEAGE_PARENT = "missing_lineage_parent"
    LINEAGE_CYCLE = "lineage_cycle"
    AMBIGUOUS_LINEAGE_BRANCH = "ambiguous_lineage_branch"
    CONFLICTING_SALE_LINKAGE = "conflicting_sale_linkage"
    CONFLICTING_INVENTORY_LINKAGE = "conflicting_inventory_linkage"
    MULTIPLE_ACTIVE_TERMINAL_EVIDENCE = "multiple_active_terminal_evidence"
    UNSUPPORTED_LIFECYCLE_TRANSITION = "unsupported_lifecycle_transition"
    CONFLICTING_QUANTITY_HISTORY = "conflicting_quantity_history"
    TIMESTAMP_CONFLICT = "timestamp_conflict"
    EVIDENCE_AFTER_AS_OF = "evidence_after_as_of"
    NON_CANONICAL_ORDERING = "non_canonical_ordering"


@dataclass(frozen=True)
class SaleCompletionEvidenceConflict:
    code: SaleCompletionEvidenceConflictCode
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class SaleCompletionEvidenceSetValid:
    status: Literal["valid"]
    evidence: tuple[SaleCompletionEvidence, ...]
    as_of: datetime


@dataclass(frozen=True)
class SaleCompletionEvidenceSetConflict:
    status: Literal["conflict"]
    conflicts: tuple[SaleCompletionEvidenceConflict, ...]
    as_of: datetime


SaleCompletionEvidenceSetValidationResult: TypeAlias = (
    SaleCompletionEvidenceSetValid | SaleCompletionEvidenceSetConflict
)

_ALLOWED_TRANSITIONS = {
    SaleCompletionLifecycleState.PENDING: {
        SaleCompletionLifecycleState.COMPLETED,
        SaleCompletionLifecycleState.CANCELLED,
        SaleCompletionLifecycleState.SUPERSEDED,
    },
    SaleCompletionLifecycleState.COMPLETED: {
        SaleCompletionLifecycleState.REFUNDED,
        SaleCompletionLifecycleState.REVERSED,
        SaleCompletionLifecycleState.SUPERSEDED,
    },
    SaleCompletionLifecycleState.CANCELLED: {SaleCompletionLifecycleState.SUPERSEDED},
    SaleCompletionLifecycleState.REFUNDED: {SaleCompletionLifecycleState.SUPERSEDED},
    SaleCompletionLifecycleState.REVERSED: {SaleCompletionLifecycleState.SUPERSEDED},
    SaleCompletionLifecycleState.SUPERSEDED: set(),
}


def _conflict(
    code: SaleCompletionEvidenceConflictCode,
    *evidence_ids: str,
) -> SaleCompletionEvidenceConflict:
    return SaleCompletionEvidenceConflict(code=code, evidence_ids=tuple(sorted(set(evidence_ids))))


def validate_sale_completion_evidence_set(
    evidence: tuple[SaleCompletionEvidence, ...],
    *,
    as_of: datetime,
    require_canonical_input_order: bool = False,
) -> SaleCompletionEvidenceSetValidationResult:
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must be timezone-aware")

    canonical = tuple(sorted(evidence, key=lambda item: item.ordering_key))
    conflicts: list[SaleCompletionEvidenceConflict] = []

    if require_canonical_input_order and evidence != canonical:
        conflicts.append(
            _conflict(
                SaleCompletionEvidenceConflictCode.NON_CANONICAL_ORDERING,
                *(item.sale_completion_evidence_id for item in evidence),
            )
        )

    by_id: dict[str, SaleCompletionEvidence] = {}
    duplicate_ids: set[str] = set()
    for item in evidence:
        if item.sale_completion_evidence_id in by_id:
            duplicate_ids.add(item.sale_completion_evidence_id)
        else:
            by_id[item.sale_completion_evidence_id] = item
    for evidence_id in sorted(duplicate_ids):
        conflicts.append(_conflict(SaleCompletionEvidenceConflictCode.DUPLICATE_EVIDENCE_IDENTITY, evidence_id))

    children: dict[str, list[SaleCompletionEvidence]] = {}
    for item in evidence:
        if item.recorded_at > as_of or (item.completed_at is not None and item.completed_at > as_of):
            conflicts.append(
                _conflict(SaleCompletionEvidenceConflictCode.EVIDENCE_AFTER_AS_OF, item.sale_completion_evidence_id)
            )
        if item.completed_at is not None and item.completed_at > item.recorded_at:
            conflicts.append(
                _conflict(SaleCompletionEvidenceConflictCode.TIMESTAMP_CONFLICT, item.sale_completion_evidence_id)
            )

        parent_id = item.lineage_parent_evidence_id
        if parent_id is None:
            continue
        children.setdefault(parent_id, []).append(item)
        parent = by_id.get(parent_id)
        if parent is None:
            conflicts.append(
                _conflict(
                    SaleCompletionEvidenceConflictCode.MISSING_LINEAGE_PARENT,
                    parent_id,
                    item.sale_completion_evidence_id,
                )
            )
            continue
        if parent.sale_id != item.sale_id:
            conflicts.append(
                _conflict(
                    SaleCompletionEvidenceConflictCode.CONFLICTING_SALE_LINKAGE,
                    parent.sale_completion_evidence_id,
                    item.sale_completion_evidence_id,
                )
            )
        if parent.inventory_id != item.inventory_id:
            conflicts.append(
                _conflict(
                    SaleCompletionEvidenceConflictCode.CONFLICTING_INVENTORY_LINKAGE,
                    parent.sale_completion_evidence_id,
                    item.sale_completion_evidence_id,
                )
            )
        if item.lifecycle_state not in _ALLOWED_TRANSITIONS[parent.lifecycle_state]:
            conflicts.append(
                _conflict(
                    SaleCompletionEvidenceConflictCode.UNSUPPORTED_LIFECYCLE_TRANSITION,
                    parent.sale_completion_evidence_id,
                    item.sale_completion_evidence_id,
                )
            )
        if (
            parent.lifecycle_state is SaleCompletionLifecycleState.COMPLETED
            and item.lifecycle_state is SaleCompletionLifecycleState.COMPLETED
            and parent.completed_unit_quantity != item.completed_unit_quantity
        ):
            conflicts.append(
                _conflict(
                    SaleCompletionEvidenceConflictCode.CONFLICTING_QUANTITY_HISTORY,
                    parent.sale_completion_evidence_id,
                    item.sale_completion_evidence_id,
                )
            )

    for parent_id, branch in sorted(children.items()):
        if len(branch) > 1:
            conflicts.append(
                _conflict(
                    SaleCompletionEvidenceConflictCode.AMBIGUOUS_LINEAGE_BRANCH,
                    parent_id,
                    *(item.sale_completion_evidence_id for item in branch),
                )
            )

    for item in evidence:
        seen: set[str] = set()
        current = item
        while current.lineage_parent_evidence_id is not None:
            parent_id = current.lineage_parent_evidence_id
            if parent_id in seen or parent_id == item.sale_completion_evidence_id:
                conflicts.append(
                    _conflict(
                        SaleCompletionEvidenceConflictCode.LINEAGE_CYCLE,
                        item.sale_completion_evidence_id,
                        parent_id,
                    )
                )
                break
            seen.add(parent_id)
            parent = by_id.get(parent_id)
            if parent is None:
                break
            current = parent

    terminal_by_scope: dict[tuple[str, str], list[SaleCompletionEvidence]] = {}
    child_ids = {child.sale_completion_evidence_id for branch in children.values() for child in branch}
    for item in evidence:
        if item.sale_completion_evidence_id not in child_ids:
            terminal_by_scope.setdefault((item.sale_id, item.inventory_id), []).append(item)
    for terminal in terminal_by_scope.values():
        if len(terminal) > 1:
            conflicts.append(
                _conflict(
                    SaleCompletionEvidenceConflictCode.MULTIPLE_ACTIVE_TERMINAL_EVIDENCE,
                    *(item.sale_completion_evidence_id for item in terminal),
                )
            )

    unique_conflicts = tuple(
        sorted(
            set(conflicts),
            key=lambda item: (item.code.value, item.evidence_ids),
        )
    )
    if unique_conflicts:
        return SaleCompletionEvidenceSetConflict(status="conflict", conflicts=unique_conflicts, as_of=as_of)
    return SaleCompletionEvidenceSetValid(status="valid", evidence=canonical, as_of=as_of)
