from datetime import datetime
from typing import Protocol, runtime_checkable

from market_intelligence.observations import ObservationKind
from market_intelligence.warehouse_models import (
    ObservationProvenance,
    WarehouseObservation,
    WarehouseSnapshot,
    WarehouseSource,
)


@runtime_checkable
class ObservationRepository(Protocol):
    """Append-only observation persistence boundary."""

    def append(self, observation: WarehouseObservation) -> None:
        """Append one immutable observation or reject a conflicting identifier."""
        ...

    def get(self, observation_id: str) -> WarehouseObservation | None:
        ...

    def list_for_product(
        self,
        product_id: str,
        *,
        source_id: str | None = None,
        kind: ObservationKind | None = None,
        observed_from: datetime | None = None,
        observed_to: datetime | None = None,
    ) -> tuple[WarehouseObservation, ...]:
        """Return observations in deterministic observed-at/id order."""
        ...


@runtime_checkable
class SourceRepository(Protocol):
    """Source and provenance registration/read boundary."""

    def register_source(self, source: WarehouseSource) -> None:
        ...

    def register_provenance(self, provenance: ObservationProvenance) -> None:
        ...

    def get_source(self, source_id: str) -> WarehouseSource | None:
        ...

    def get_provenance(self, provenance_id: str) -> ObservationProvenance | None:
        ...


@runtime_checkable
class SnapshotRepository(Protocol):
    """Immutable warehouse snapshot boundary."""

    def append(self, snapshot: WarehouseSnapshot) -> None:
        ...

    def get(self, snapshot_id: str) -> WarehouseSnapshot | None:
        ...

    def list_captured_between(
        self,
        captured_from: datetime | None = None,
        captured_to: datetime | None = None,
    ) -> tuple[WarehouseSnapshot, ...]:
        """Return snapshots in deterministic captured-at/id order."""
        ...


@runtime_checkable
class PreviewHistoryRepository(Protocol):
    """Read-only saved-query preview-history boundary."""

    def list_observations(
        self,
        saved_query_id: str,
        *,
        captured_from: datetime | None = None,
        captured_to: datetime | None = None,
    ) -> tuple[WarehouseObservation, ...]:
        """Return persisted preview evidence without executing a provider query."""
        ...
