import sqlite3
from typing import Optional, Sequence


class SettlementAllocationConflict(RuntimeError):
    pass


class SettlementAllocationRepository:
    """Append-only persistence and queries for settlement allocation authority."""

    def parent_by_id(self, c: sqlite3.Connection, settlement_evidence_id: str) -> Optional[sqlite3.Row]:
        return c.execute("SELECT * FROM settlement_evidence WHERE settlement_evidence_id=?", (settlement_evidence_id,)).fetchone()

    def line_by_id(self, c: sqlite3.Connection, allocation_line_id: str) -> Optional[sqlite3.Row]:
        return c.execute("SELECT * FROM settlement_allocation_evidence WHERE allocation_line_id=?", (allocation_line_id,)).fetchone()

    def lines_for_group(self, c: sqlite3.Connection, allocation_group_id: str) -> Sequence[sqlite3.Row]:
        return c.execute("SELECT * FROM settlement_allocation_evidence WHERE allocation_group_id=? ORDER BY created_at, allocation_line_id", (allocation_group_id,)).fetchall()

    def revision_by_id(self, c: sqlite3.Connection, revision_id: str) -> Optional[sqlite3.Row]:
        return c.execute("SELECT * FROM settlement_allocation_revisions WHERE revision_id=?", (revision_id,)).fetchone()

    def revisions_for_evidence(self, c: sqlite3.Connection, allocation_evidence_id: str) -> Sequence[sqlite3.Row]:
        return c.execute("SELECT * FROM settlement_allocation_revisions WHERE allocation_evidence_id=? ORDER BY created_at, revision_id", (allocation_evidence_id,)).fetchall()

    def current_revisions_for_evidence(self, c: sqlite3.Connection, allocation_evidence_id: str) -> Sequence[sqlite3.Row]:
        return c.execute("SELECT * FROM settlement_allocation_revisions WHERE allocation_evidence_id=? AND current_revision_flag='Y' ORDER BY created_at, revision_id", (allocation_evidence_id,)).fetchall()

    def append_revision(self, c: sqlite3.Connection, *, allocation_evidence_id: str, revision_id: str,
                        supersedes_revision_id: Optional[str], current_revision_flag: str, revision_status: str,
                        created_event_id: str, created_at: str) -> sqlite3.Row:
        values = (revision_id, allocation_evidence_id, supersedes_revision_id, current_revision_flag, revision_status, created_event_id, created_at)
        prior = self.revision_by_id(c, revision_id)
        if prior is not None:
            columns = ("revision_id", "allocation_evidence_id", "supersedes_revision_id", "current_revision_flag", "revision_status", "created_event_id", "created_at")
            if tuple(prior[column] for column in columns) != values:
                raise SettlementAllocationConflict("Contradictory allocation revision replay blocked")
            return prior
        c.execute("INSERT INTO settlement_allocation_revisions(revision_id,allocation_evidence_id,supersedes_revision_id,current_revision_flag,revision_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?)", values)
        row = self.revision_by_id(c, revision_id)
        if row is None:
            raise SettlementAllocationConflict("Allocation revision persistence verification failed")
        return row

    def lock_by_evidence_id(self, c: sqlite3.Connection, allocation_evidence_id: str) -> Optional[sqlite3.Row]:
        return c.execute("SELECT * FROM settlement_allocation_locks WHERE allocation_evidence_id=?", (allocation_evidence_id,)).fetchone()

    def append_evidence_lock(self, c: sqlite3.Connection, *, allocation_evidence_id: str, evidence_lock_status: str,
                             lock_effective_date: str, locked_by_authority: str, lock_reason: str,
                             unlock_request_status: str, audit_preservation_result: str,
                             created_event_id: str, created_at: str) -> sqlite3.Row:
        line = self.line_by_id(c, allocation_evidence_id)
        if line is None:
            raise SettlementAllocationConflict("Allocation evidence lock lifecycle verification failed")
        cross_check = self.latest_cross_check_for_group(c, str(line["allocation_group_id"]))
        lock_eligible = (cross_check is not None and cross_check["cross_check_status"] == "ALLOCATION CROSS-CHECKED" and int(cross_check["allocation_remainder_minor"]) == 0)
        if evidence_lock_status == "LOCKED" and not lock_eligible:
            raise SettlementAllocationConflict("Allocation evidence lock blocked: lifecycle is not LOCK ELIGIBLE")
        values = (allocation_evidence_id, evidence_lock_status, lock_effective_date, locked_by_authority, lock_reason, unlock_request_status, audit_preservation_result, created_event_id, created_at)
        prior = self.lock_by_evidence_id(c, allocation_evidence_id)
        columns = ("allocation_evidence_id", "evidence_lock_status", "lock_effective_date", "locked_by_authority", "lock_reason", "unlock_request_status", "audit_preservation_result", "created_event_id", "created_at")
        if prior is not None:
            if tuple(prior[column] for column in columns) != values:
                raise SettlementAllocationConflict("Contradictory allocation evidence lock replay blocked")
            return prior
        c.execute("INSERT INTO settlement_allocation_locks(allocation_evidence_id,evidence_lock_status,lock_effective_date,locked_by_authority,lock_reason,unlock_request_status,audit_preservation_result,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)", values)
        row = self.lock_by_evidence_id(c, allocation_evidence_id)
        if row is None:
            raise SettlementAllocationConflict("Allocation evidence lock persistence verification failed")
        return row

    def cross_check_by_id(self, c: sqlite3.Connection, cross_check_id: str) -> Optional[sqlite3.Row]:
        return c.execute("SELECT * FROM settlement_allocation_cross_checks WHERE cross_check_id=?", (cross_check_id,)).fetchone()

    def latest_cross_check_for_group(self, c: sqlite3.Connection, allocation_group_id: str) -> Optional[sqlite3.Row]:
        row = c.execute("SELECT * FROM settlement_allocation_cross_checks WHERE allocation_group_id=? ORDER BY created_at DESC, cross_check_id DESC LIMIT 1", (allocation_group_id,)).fetchone()
        if row is None:
            return None
        lines = self.lines_for_group(c, allocation_group_id)
        if not lines or any(str(line["created_at"]) > str(row["created_at"]) for line in lines):
            return None
        if any(line["allocated_amount_minor"] is None for line in lines):
            return None
        current_total = sum(int(line["allocated_amount_minor"]) for line in lines)
        if current_total != int(row["allocation_group_total_minor"]):
            return None
        return row

    def sale_marketplace(self, c: sqlite3.Connection, sale_id: str) -> Optional[str]:
        row = c.execute("SELECT marketplace FROM publication_lifecycle_events WHERE sale_id=? AND event_type='SOLD_CONVERSION' ORDER BY created_at DESC LIMIT 1", (sale_id,)).fetchone()
        return None if row is None else str(row["marketplace"])

    def attribution_readiness_by_event(self, c: sqlite3.Connection, event_id: str) -> Optional[sqlite3.Row]:
        return c.execute("SELECT * FROM audit_events WHERE event_id=? AND authority_type='SETTLEMENT_ATTRIBUTION_READINESS'", (event_id,)).fetchone()

    def append_attribution_readiness(self, c: sqlite3.Connection, *, event_id: str, sale_id: str, allocation_group_id: str, recorded_at: str) -> sqlite3.Row:
        authority_id = f"{sale_id}:{allocation_group_id}"
        result = "READY FOR SETTLEMENT ATTRIBUTION"
        prior = self.attribution_readiness_by_event(c, event_id)
        if prior is not None:
            expected = (event_id, "SETTLEMENT_ATTRIBUTION_READINESS", authority_id, result, recorded_at)
            actual = tuple(prior[column] for column in ("event_id", "authority_type", "authority_id", "verification_result", "recorded_at"))
            if actual != expected:
                raise SettlementAllocationConflict("Contradictory settlement attribution readiness replay blocked")
            return prior
        c.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)", (event_id, "SETTLEMENT_ATTRIBUTION_READINESS", authority_id, result, recorded_at))
        row = self.attribution_readiness_by_event(c, event_id)
        if row is None:
            raise SettlementAllocationConflict("Settlement attribution readiness persistence verification failed")
        return row

    def append_line(self, c: sqlite3.Connection, *, allocation_group_id: str, allocation_line_id: str,
                    settlement_evidence_id: str, linked_sale_id: Optional[str], source_traceability: str,
                    evidence_date: str, currency: str, component_type: str, allocated_amount_minor: Optional[int],
                    notes: str, allocation_status: str, created_event_id: str, created_at: str) -> sqlite3.Row:
        group_parent = c.execute("SELECT settlement_evidence_id FROM settlement_allocation_evidence WHERE allocation_group_id=? LIMIT 1", (allocation_group_id,)).fetchone()
        if group_parent is not None and group_parent["settlement_evidence_id"] != settlement_evidence_id:
            raise SettlementAllocationConflict("Allocation group re-parenting blocked")
        values = (allocation_group_id, allocation_line_id, settlement_evidence_id, linked_sale_id, source_traceability, evidence_date, currency, component_type, allocated_amount_minor, notes, allocation_status, created_event_id, created_at)
        prior = self.line_by_id(c, allocation_line_id)
        if prior is not None:
            columns = ("allocation_group_id", "allocation_line_id", "settlement_evidence_id", "linked_sale_id", "source_traceability", "evidence_date", "currency", "component_type", "allocated_amount_minor", "notes", "allocation_status", "created_event_id", "created_at")
            if tuple(prior[column] for column in columns) != values:
                raise SettlementAllocationConflict("Contradictory allocation evidence blocked")
            return prior
        c.execute("INSERT INTO settlement_allocation_evidence(allocation_group_id,allocation_line_id,settlement_evidence_id,linked_sale_id,source_traceability,evidence_date,currency,component_type,allocated_amount_minor,notes,allocation_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
        row = self.line_by_id(c, allocation_line_id)
        if row is None:
            raise SettlementAllocationConflict("Allocation evidence persistence verification failed")
        return row

    def append_cross_check(self, c: sqlite3.Connection, *, cross_check_id: str, allocation_group_id: str,
                           settlement_evidence_id: str, allocation_group_total_minor: int, settlement_net_minor: int,
                           allocation_remainder_minor: int, cross_check_status: str, created_event_id: str, created_at: str) -> sqlite3.Row:
        values = (cross_check_id, allocation_group_id, settlement_evidence_id, int(allocation_group_total_minor), int(settlement_net_minor), int(allocation_remainder_minor), cross_check_status, created_event_id, created_at)
        prior = self.cross_check_by_id(c, cross_check_id)
        if prior is not None:
            columns = ("cross_check_id", "allocation_group_id", "settlement_evidence_id", "allocation_group_total_minor", "settlement_net_minor", "allocation_remainder_minor", "cross_check_status", "created_event_id", "created_at")
            if tuple(prior[column] for column in columns) != values:
                raise SettlementAllocationConflict("Contradictory allocation cross-check blocked")
            return prior
        c.execute("INSERT INTO settlement_allocation_cross_checks(cross_check_id,allocation_group_id,settlement_evidence_id,allocation_group_total_minor,settlement_net_minor,allocation_remainder_minor,cross_check_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)", values)
        row = self.cross_check_by_id(c, cross_check_id)
        if row is None:
            raise SettlementAllocationConflict("Allocation cross-check persistence verification failed")
        return row
