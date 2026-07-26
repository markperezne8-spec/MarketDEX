from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from core.sale_completion import (
    SaleCompletionAvailable,
    SaleCompletionCompleteness,
    SaleCompletionConflict,
    SaleCompletionCoverage,
    SaleCompletionEvidence,
    SaleCompletionQuery,
    SaleCompletionQueryResult,
    SaleCompletionUnavailable,
)
from core.sale_completion_validation import (
    SaleCompletionEvidenceConflict,
    SaleCompletionEvidenceSetConflict,
    SaleCompletionEvidenceSetValid,
    validate_sale_completion_evidence_set,
)


@dataclass(frozen=True)
class SaleCompletionRepositoryDiagnostic:
    conflicts: tuple[SaleCompletionEvidenceConflict, ...]

    @property
    def evidence_ids(self) -> tuple[str, ...]:
        return tuple(sorted({evidence_id for conflict in self.conflicts for evidence_id in conflict.evidence_ids}))


@dataclass(frozen=True)
class SaleCompletionRepositoryRead:
    result: SaleCompletionQueryResult
    diagnostic: SaleCompletionRepositoryDiagnostic | None = None


@runtime_checkable
class SaleCompletionRepository(Protocol):
    def query_sale_completion(self, query: SaleCompletionQuery) -> SaleCompletionRepositoryRead: ...


def build_sale_completion_repository_read(
    *,
    query: SaleCompletionQuery,
    evidence: tuple[SaleCompletionEvidence, ...],
    source_systems: tuple[str, ...],
    coverage_complete: bool,
    unavailable_reason_code: str = "coverage_unavailable",
) -> SaleCompletionRepositoryRead:
    completeness = (
        SaleCompletionCompleteness.COMPLETE
        if coverage_complete
        else SaleCompletionCompleteness.UNAVAILABLE
    )
    coverage = SaleCompletionCoverage(
        requested_inventory_ids=query.inventory_ids,
        requested_sale_ids=query.sale_ids,
        source_systems=tuple(sorted(set(source_systems))),
        as_of=query.as_of,
        evidence_count=len(evidence),
        completeness=completeness,
        completed_from=query.completed_from,
        completed_until=query.completed_until,
    )

    if not coverage_complete:
        return SaleCompletionRepositoryRead(
            result=SaleCompletionUnavailable(
                status="unavailable",
                reason_code=unavailable_reason_code,
                coverage=coverage,
            )
        )

    validation = validate_sale_completion_evidence_set(evidence, as_of=query.as_of)
    if isinstance(validation, SaleCompletionEvidenceSetConflict):
        conflict_coverage = SaleCompletionCoverage(
            requested_inventory_ids=query.inventory_ids,
            requested_sale_ids=query.sale_ids,
            source_systems=coverage.source_systems,
            as_of=query.as_of,
            evidence_count=len(evidence),
            completeness=SaleCompletionCompleteness.CONFLICTING,
            completed_from=query.completed_from,
            completed_until=query.completed_until,
        )
        return SaleCompletionRepositoryRead(
            result=SaleCompletionConflict(
                status="conflict",
                reason_code="evidence_validation_conflict",
                coverage=conflict_coverage,
            ),
            diagnostic=SaleCompletionRepositoryDiagnostic(conflicts=validation.conflicts),
        )

    if not isinstance(validation, SaleCompletionEvidenceSetValid):
        raise TypeError("unexpected sale-completion validation result")

    return SaleCompletionRepositoryRead(
        result=SaleCompletionAvailable(
            status="available",
            evidence=validation.evidence,
            coverage=coverage,
        )
    )
