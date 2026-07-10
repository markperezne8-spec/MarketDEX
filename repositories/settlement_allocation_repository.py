import sqlite3
from typing import Optional, Sequence


class SettlementAllocationConflict(RuntimeError):
    pass


class SettlementAllocationRepository:
    """Append-only persistence for Build 498 settlement allocation evidence intake."""

    def parent_by_id(self, c: sqlite3.Connection, settlement_evidence_id: str) -> Optional[sqlite3.Row]:
        return c.execute(
            "SELECT * FROM settlement_evidence WHERE settlement_evidence_id=?",
            (settlement_evidence_id,),
        ).fetchone()

    def line_by_id(self, c: sqlite3.Connection, allocation_line_id: str) -> Optional[sqlite3.Row]:
        return c.execute(
            "SELECT * FROM settlement_allocation_evidence WHERE allocation_line_id=?",
            (allocation_line_id,),
        ).fetchone()

    def lines_for_group(self, c: sqlite3.Connection, allocation_group_id: str) -> Sequence[sqlite3.Row]:
        return c.execute(
            "SELECT * FROM settlement_allocation_evidence WHERE allocation_group_id=? ORDER BY created_at, allocation_line_id",
            (allocation_group_id,),
        ).fetchall()

    def sale_marketplace(self, c: sqlite3.Connection, sale_id: str) -> Optional[str]:
        row = c.execute(
            """SELECT marketplace FROM publication_lifecycle_events
               WHERE sale_id=? AND event_type='SOLD_CONVERSION'
               ORDER BY created_at DESC LIMIT 1""",
            (sale_id,),
        ).fetchone()
        return None if row is None else str(row["marketplace"])

    def append_line(self, c: sqlite3.Connection, *, allocation_group_id: str,
                    allocation_line_id: str, settlement_evidence_id: str,
                    linked_sale_id: Optional[str], source_traceability: str,
                    evidence_date: str, currency: str, component_type: str,
                    allocated_amount_minor: Optional[int], notes: str,
                    allocation_status: str, created_event_id: str,
                    created_at: str) -> sqlite3.Row:
        group_parent = c.execute(
            """SELECT settlement_evidence_id FROM settlement_allocation_evidence
               WHERE allocation_group_id=? LIMIT 1""",
            (allocation_group_id,),
        ).fetchone()
        if group_parent is not None and group_parent["settlement_evidence_id"] != settlement_evidence_id:
            raise SettlementAllocationConflict("Allocation group re-parenting blocked")

        values = (
            allocation_group_id, allocation_line_id, settlement_evidence_id,
            linked_sale_id, source_traceability, evidence_date, currency,
            component_type, allocated_amount_minor, notes, allocation_status,
            created_event_id, created_at,
        )
        prior = self.line_by_id(c, allocation_line_id)
        if prior is not None:
            columns = (
                "allocation_group_id", "allocation_line_id", "settlement_evidence_id",
                "linked_sale_id", "source_traceability", "evidence_date", "currency",
                "component_type", "allocated_amount_minor", "notes", "allocation_status",
                "created_event_id", "created_at",
            )
            if tuple(prior[column] for column in columns) != values:
                raise SettlementAllocationConflict("Contradictory allocation evidence blocked")
            return prior

        c.execute(
            """INSERT INTO settlement_allocation_evidence(
               allocation_group_id,allocation_line_id,settlement_evidence_id,
               linked_sale_id,source_traceability,evidence_date,currency,component_type,
               allocated_amount_minor,notes,allocation_status,created_event_id,created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            values,
        )
        row = self.line_by_id(c, allocation_line_id)
        if row is None:
            raise SettlementAllocationConflict("Allocation evidence persistence verification failed")
        return row
