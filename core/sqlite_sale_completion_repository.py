from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from core.database_manager import DatabaseManager
from core.sale_completion import (
    SaleCompletionCompleteness,
    SaleCompletionConflict,
    SaleCompletionCoverage,
    SaleCompletionEvidence,
    SaleCompletionLifecycleState,
    SaleCompletionQuery,
    SaleCompletionUnavailable,
)
from core.sale_completion_repository import (
    SaleCompletionRepositoryRead,
    build_sale_completion_repository_read,
)


@dataclass(frozen=True)
class SaleCompletionAdapterDiagnostic:
    reason_code: str
    row_identity: str | None
    detail: str


class SqliteSalesSaleCompletionRepository:
    SOURCE_SYSTEM = "sqlite.sales"

    def __init__(self, database_manager: DatabaseManager) -> None:
        self._database_manager = database_manager

    def query_sale_completion(self, query: SaleCompletionQuery) -> SaleCompletionRepositoryRead:
        sql, parameters = self._build_query(query)
        try:
            with self._database_manager.read_connection() as connection:
                rows = tuple(connection.execute(sql, parameters).fetchall())
        except Exception:
            coverage = self._coverage(
                query=query,
                evidence_count=0,
                completeness=SaleCompletionCompleteness.UNAVAILABLE,
            )
            return SaleCompletionRepositoryRead(
                result=SaleCompletionUnavailable(
                    status="unavailable",
                    reason_code="sqlite_sales_read_unavailable",
                    coverage=coverage,
                )
            )

        evidence: list[SaleCompletionEvidence] = []
        for row in rows:
            try:
                evidence.append(self._decode_row(row))
            except (KeyError, TypeError, ValueError) as exc:
                coverage = self._coverage(
                    query=query,
                    evidence_count=len(rows),
                    completeness=SaleCompletionCompleteness.CONFLICTING,
                )
                diagnostic = SaleCompletionAdapterDiagnostic(
                    reason_code="sqlite_sales_row_decode_conflict",
                    row_identity=self._row_identity(row),
                    detail=str(exc),
                )
                return SaleCompletionRepositoryRead(
                    result=SaleCompletionConflict(
                        status="conflict",
                        reason_code=diagnostic.reason_code,
                        coverage=coverage,
                    ),
                    diagnostic=diagnostic,  # type: ignore[arg-type]
                )

        return build_sale_completion_repository_read(
            query=query,
            evidence=tuple(evidence),
            source_systems=(self.SOURCE_SYSTEM,),
            coverage_complete=True,
        )

    @staticmethod
    def _build_query(query: SaleCompletionQuery) -> tuple[str, tuple[Any, ...]]:
        identity_clauses: list[str] = []
        parameters: list[Any] = []
        if query.inventory_ids:
            placeholders = ",".join("?" for _ in query.inventory_ids)
            identity_clauses.append(f"asset_id IN ({placeholders})")
            parameters.extend(query.inventory_ids)
        if query.sale_ids:
            placeholders = ",".join("?" for _ in query.sale_ids)
            identity_clauses.append(f"sale_id IN ({placeholders})")
            parameters.extend(query.sale_ids)

        clauses = [f"({' OR '.join(identity_clauses)})", "state = ?", "created_at <= ?"]
        parameters.extend(("COMPLETED", query.as_of.isoformat()))
        if query.completed_from is not None and query.completed_until is not None:
            clauses.extend(("created_at >= ?", "created_at < ?"))
            parameters.extend((query.completed_from.isoformat(), query.completed_until.isoformat()))

        sql = (
            "SELECT sale_id, asset_id, quantity, state, created_event_id, created_at "
            "FROM sales WHERE " + " AND ".join(clauses) + " ORDER BY created_at, sale_id, asset_id, created_event_id"
        )
        return sql, tuple(parameters)

    @classmethod
    def _decode_row(cls, row: Any) -> SaleCompletionEvidence:
        state = str(row["state"])
        if state != "COMPLETED":
            raise ValueError(f"unsupported sales state: {state}")
        completed_at = datetime.fromisoformat(str(row["created_at"]))
        if completed_at.tzinfo is None or completed_at.utcoffset() is None:
            raise ValueError("sales created_at must be timezone-aware")
        return SaleCompletionEvidence(
            sale_completion_evidence_id=str(row["created_event_id"]),
            sale_id=str(row["sale_id"]),
            inventory_id=str(row["asset_id"]),
            lifecycle_state=SaleCompletionLifecycleState.COMPLETED,
            source_system=cls.SOURCE_SYSTEM,
            recorded_at=completed_at,
            completed_unit_quantity=row["quantity"],
            completed_at=completed_at,
        )

    @classmethod
    def _coverage(
        cls,
        *,
        query: SaleCompletionQuery,
        evidence_count: int,
        completeness: SaleCompletionCompleteness,
    ) -> SaleCompletionCoverage:
        return SaleCompletionCoverage(
            requested_inventory_ids=query.inventory_ids,
            requested_sale_ids=query.sale_ids,
            source_systems=(cls.SOURCE_SYSTEM,),
            as_of=query.as_of,
            evidence_count=evidence_count,
            completeness=completeness,
            completed_from=query.completed_from,
            completed_until=query.completed_until,
        )

    @staticmethod
    def _row_identity(row: Any) -> str | None:
        try:
            return str(row["sale_id"])
        except (KeyError, IndexError, TypeError):
            return None
