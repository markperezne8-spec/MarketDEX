from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal, TypeAlias


def _require_text(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _require_aware_datetime(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


class SaleCompletionLifecycleState(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    REVERSED = "reversed"
    SUPERSEDED = "superseded"


class SaleCompletionCompleteness(str, Enum):
    COMPLETE = "complete"
    UNAVAILABLE = "unavailable"
    CONFLICTING = "conflicting"


@dataclass(frozen=True)
class SaleCompletionEvidence:
    sale_completion_evidence_id: str
    sale_id: str
    inventory_id: str
    lifecycle_state: SaleCompletionLifecycleState
    source_system: str
    recorded_at: datetime
    lineage_parent_evidence_id: str | None = None
    completed_unit_quantity: int | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "sale_completion_evidence_id",
            _require_text(self.sale_completion_evidence_id, "sale_completion_evidence_id"),
        )
        object.__setattr__(self, "sale_id", _require_text(self.sale_id, "sale_id"))
        object.__setattr__(self, "inventory_id", _require_text(self.inventory_id, "inventory_id"))
        object.__setattr__(self, "source_system", _require_text(self.source_system, "source_system"))
        _require_aware_datetime(self.recorded_at, "recorded_at")

        if not isinstance(self.lifecycle_state, SaleCompletionLifecycleState):
            raise ValueError("lifecycle_state must be a SaleCompletionLifecycleState")

        if self.lineage_parent_evidence_id is not None:
            parent = _require_text(self.lineage_parent_evidence_id, "lineage_parent_evidence_id")
            if parent == self.sale_completion_evidence_id:
                raise ValueError("lineage_parent_evidence_id cannot reference the same evidence")
            object.__setattr__(self, "lineage_parent_evidence_id", parent)

        lineage_required = {
            SaleCompletionLifecycleState.REFUNDED,
            SaleCompletionLifecycleState.REVERSED,
            SaleCompletionLifecycleState.SUPERSEDED,
        }
        if self.lifecycle_state in lineage_required and self.lineage_parent_evidence_id is None:
            raise ValueError(f"{self.lifecycle_state.value} evidence requires lineage_parent_evidence_id")

        if self.lifecycle_state is SaleCompletionLifecycleState.COMPLETED:
            if type(self.completed_unit_quantity) is not int or self.completed_unit_quantity <= 0:
                raise ValueError("completed evidence requires a positive whole-unit quantity")
            if self.completed_at is None:
                raise ValueError("completed evidence requires completed_at")
            _require_aware_datetime(self.completed_at, "completed_at")
        elif self.completed_unit_quantity is not None or self.completed_at is not None:
            raise ValueError("only completed evidence may carry completion quantity or completed_at")

    @property
    def ordering_key(self) -> tuple[datetime, datetime, str, str, str]:
        effective_time = self.completed_at or self.recorded_at
        return (
            effective_time,
            self.recorded_at,
            self.sale_id,
            self.inventory_id,
            self.sale_completion_evidence_id,
        )


@dataclass(frozen=True)
class SaleCompletionQuery:
    inventory_ids: tuple[str, ...]
    sale_ids: tuple[str, ...]
    as_of: datetime
    completed_from: datetime | None = None
    completed_until: datetime | None = None

    def __post_init__(self) -> None:
        inventory_ids = tuple(_require_text(value, "inventory_id") for value in self.inventory_ids)
        sale_ids = tuple(_require_text(value, "sale_id") for value in self.sale_ids)
        if not inventory_ids and not sale_ids:
            raise ValueError("at least one inventory_id or sale_id is required")
        if len(set(inventory_ids)) != len(inventory_ids) or len(set(sale_ids)) != len(sale_ids):
            raise ValueError("query identities must be unique")
        object.__setattr__(self, "inventory_ids", inventory_ids)
        object.__setattr__(self, "sale_ids", sale_ids)
        _require_aware_datetime(self.as_of, "as_of")

        if (self.completed_from is None) != (self.completed_until is None):
            raise ValueError("completed_from and completed_until must be supplied together")
        if self.completed_from is not None and self.completed_until is not None:
            _require_aware_datetime(self.completed_from, "completed_from")
            _require_aware_datetime(self.completed_until, "completed_until")
            if self.completed_from >= self.completed_until:
                raise ValueError("completed_from must be earlier than completed_until")
            if self.completed_until > self.as_of:
                raise ValueError("completed_until cannot be later than as_of")


@dataclass(frozen=True)
class SaleCompletionCoverage:
    requested_inventory_ids: tuple[str, ...]
    requested_sale_ids: tuple[str, ...]
    source_systems: tuple[str, ...]
    as_of: datetime
    evidence_count: int
    completeness: SaleCompletionCompleteness
    completed_from: datetime | None = None
    completed_until: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "requested_inventory_ids",
            tuple(_require_text(value, "requested_inventory_id") for value in self.requested_inventory_ids),
        )
        object.__setattr__(
            self,
            "requested_sale_ids",
            tuple(_require_text(value, "requested_sale_id") for value in self.requested_sale_ids),
        )
        object.__setattr__(
            self,
            "source_systems",
            tuple(_require_text(value, "source_system") for value in self.source_systems),
        )
        _require_aware_datetime(self.as_of, "as_of")
        if type(self.evidence_count) is not int or self.evidence_count < 0:
            raise ValueError("evidence_count must be a non-negative integer")
        if not isinstance(self.completeness, SaleCompletionCompleteness):
            raise ValueError("completeness must be a SaleCompletionCompleteness")
        if (self.completed_from is None) != (self.completed_until is None):
            raise ValueError("coverage range boundaries must be supplied together")
        if self.completed_from is not None and self.completed_until is not None:
            _require_aware_datetime(self.completed_from, "completed_from")
            _require_aware_datetime(self.completed_until, "completed_until")
            if self.completed_from >= self.completed_until:
                raise ValueError("completed_from must be earlier than completed_until")


@dataclass(frozen=True)
class SaleCompletionAvailable:
    status: Literal["available"]
    evidence: tuple[SaleCompletionEvidence, ...]
    coverage: SaleCompletionCoverage

    def __post_init__(self) -> None:
        if self.status != "available":
            raise ValueError("available result status must be 'available'")
        if self.coverage.completeness is not SaleCompletionCompleteness.COMPLETE:
            raise ValueError("available result requires complete coverage")
        if self.coverage.evidence_count != len(self.evidence):
            raise ValueError("coverage evidence_count must match evidence length")
        if tuple(sorted(self.evidence, key=lambda item: item.ordering_key)) != self.evidence:
            raise ValueError("available evidence must use deterministic canonical ordering")


@dataclass(frozen=True)
class SaleCompletionUnavailable:
    status: Literal["unavailable"]
    reason_code: str
    coverage: SaleCompletionCoverage

    def __post_init__(self) -> None:
        if self.status != "unavailable":
            raise ValueError("unavailable result status must be 'unavailable'")
        object.__setattr__(self, "reason_code", _require_text(self.reason_code, "reason_code"))
        if self.coverage.completeness is not SaleCompletionCompleteness.UNAVAILABLE:
            raise ValueError("unavailable result requires unavailable coverage")


@dataclass(frozen=True)
class SaleCompletionConflict:
    status: Literal["conflict"]
    reason_code: str
    coverage: SaleCompletionCoverage

    def __post_init__(self) -> None:
        if self.status != "conflict":
            raise ValueError("conflict result status must be 'conflict'")
        object.__setattr__(self, "reason_code", _require_text(self.reason_code, "reason_code"))
        if self.coverage.completeness is not SaleCompletionCompleteness.CONFLICTING:
            raise ValueError("conflict result requires conflicting coverage")


SaleCompletionQueryResult: TypeAlias = (
    SaleCompletionAvailable | SaleCompletionUnavailable | SaleCompletionConflict
)
