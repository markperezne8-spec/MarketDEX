import sqlite3
from typing import Optional

from core.database_manager import DatabaseManager
from repositories.settlement_allocation_repository import SettlementAllocationRepository


class SettlementAllocationNotReady(RuntimeError):
    pass


class SettlementAllocationService:
    """Builds 498-503 settlement allocation authority."""

    ACTIVE_REVISION_AUTHORITY = "ACTIVE REVISION AUTHORITY ONLY — NO TAX, RECONCILIATION, OR SETTLEMENT COMPLETION AUTHORITY"
    NO_REVISION_AUTHORITY = "NO REVISION AUTHORITY — FAIL CLOSED"
    LOCK_AUTHORITY_ONLY = "LOCK AUTHORITY ONLY"
    NO_LIFECYCLE_AUTHORITY = "NO LIFECYCLE AUTHORITY — FAIL CLOSED"

    def __init__(self, database: DatabaseManager, repository: Optional[SettlementAllocationRepository] = None) -> None:
        self.database = database
        self.repository = repository or SettlementAllocationRepository()

    @staticmethod
    def _required(value: object) -> bool:
        return value is not None and str(value).strip() != ""

    def allocation_group_lifecycle(self, allocation_group_id: str) -> dict:
        if not self._required(allocation_group_id):
            raise SettlementAllocationNotReady("NO LIFECYCLE AUTHORITY — FAIL CLOSED: allocation group identity is blank")
        with self.database.read_connection() as c:
            lines = self.repository.lines_for_group(c, allocation_group_id)
            cross_check = self.repository.latest_cross_check_for_group(c, allocation_group_id)
            if cross_check is not None and cross_check["cross_check_status"] == "ALLOCATION EXCEPTION":
                state, transition, boundary = "EXCEPTION", "FAIL CLOSED", self.NO_LIFECYCLE_AUTHORITY
            elif cross_check is not None and cross_check["cross_check_status"] == "ALLOCATION CROSS-CHECKED" and int(cross_check["allocation_remainder_minor"]) == 0:
                state, transition, boundary = "CROSS-CHECKED", "LOCK ELIGIBLE", self.LOCK_AUTHORITY_ONLY
            elif lines:
                state, transition, boundary = "EVIDENCE PENDING", "PENDING", self.NO_LIFECYCLE_AUTHORITY
            else:
                state, transition, boundary = "DRAFT", "PENDING", self.NO_LIFECYCLE_AUTHORITY
            return {"allocation_group_id": allocation_group_id, "lifecycle_state": state,
                    "transition_result": transition, "lifecycle_authority_boundary": boundary}

    def record_revision(self, *, allocation_evidence_id: str, revision_id: str, current_revision_flag: str,
                        created_event_id: str, created_at: str,
                        supersedes_revision_id: Optional[str] = None) -> dict:
        required = (allocation_evidence_id, revision_id, created_event_id, created_at)
        if not all(self._required(value) for value in required):
            raise SettlementAllocationNotReady("NO REVISION AUTHORITY — FAIL CLOSED: required revision evidence is blank")
        if current_revision_flag not in ("Y", ""):
            raise SettlementAllocationNotReady("NO REVISION AUTHORITY — FAIL CLOSED: current revision flag is not canonical")
        supersedes = None if not self._required(supersedes_revision_id) else str(supersedes_revision_id).strip()
        status = "ACTIVE" if current_revision_flag == "Y" else ("REVISED" if supersedes is not None else "INITIAL")
        with self.database.transaction() as c:
            if self.repository.line_by_id(c, allocation_evidence_id) is None:
                raise SettlementAllocationNotReady("NO REVISION AUTHORITY — FAIL CLOSED: allocation evidence is missing")
            if supersedes is not None:
                prior = self.repository.revision_by_id(c, supersedes)
                if prior is None or prior["allocation_evidence_id"] != allocation_evidence_id or supersedes == revision_id:
                    raise SettlementAllocationNotReady("NO REVISION AUTHORITY — FAIL CLOSED: supersedes revision linkage is invalid")
            row = self.repository.append_revision(c, allocation_evidence_id=allocation_evidence_id,
                revision_id=revision_id, supersedes_revision_id=supersedes,
                current_revision_flag=current_revision_flag, revision_status=status,
                created_event_id=created_event_id, created_at=created_at)
            current = self.repository.current_revisions_for_evidence(c, allocation_evidence_id)
            conflict = "CONFLICT" if len(current) > 1 else "NO CONFLICT"
            boundary = self.ACTIVE_REVISION_AUTHORITY if current_revision_flag == "Y" and conflict == "NO CONFLICT" else self.NO_REVISION_AUTHORITY
            return {"allocation_evidence_id": row["allocation_evidence_id"], "revision_id": row["revision_id"],
                    "supersedes_revision_id": row["supersedes_revision_id"], "current_revision_flag": row["current_revision_flag"],
                    "revision_status": row["revision_status"], "revision_conflict": conflict,
                    "revision_authority_boundary": boundary}

    def revision_authority(self, allocation_evidence_id: str) -> dict:
        if not self._required(allocation_evidence_id):
            raise SettlementAllocationNotReady("NO REVISION AUTHORITY — FAIL CLOSED: allocation evidence identity is blank")
        with self.database.read_connection() as c:
            revisions = self.repository.revisions_for_evidence(c, allocation_evidence_id)
            current = self.repository.current_revisions_for_evidence(c, allocation_evidence_id)
            conflict = "CONFLICT" if len(current) > 1 else "NO CONFLICT"
            if len(current) != 1 or conflict != "NO CONFLICT":
                return {"allocation_evidence_id": allocation_evidence_id, "revision_conflict": conflict,
                        "revision_authority_boundary": self.NO_REVISION_AUTHORITY, "current_revision": None}
            row = current[0]
            return {"allocation_evidence_id": allocation_evidence_id, "revision_conflict": conflict,
                    "revision_authority_boundary": self.ACTIVE_REVISION_AUTHORITY, "current_revision": dict(row),
                    "revision_count": len(revisions)}

    def record_evidence_lock(self, *, allocation_evidence_id: str, lock_effective_date: str,
                             locked_by_authority: str, lock_reason: str, created_event_id: str,
                             created_at: str) -> dict:
        required = (allocation_evidence_id, created_event_id, created_at)
        if not all(self._required(value) for value in required):
            raise SettlementAllocationNotReady("NO LOCK AUTHORITY — FAIL CLOSED: required lock evidence is blank")
        if locked_by_authority not in ("Y", ""):
            raise SettlementAllocationNotReady("NO LOCK AUTHORITY — FAIL CLOSED: locked by authority is not canonical")
        if locked_by_authority == "Y" and not self._required(lock_effective_date):
            raise SettlementAllocationNotReady("NO LOCK AUTHORITY — FAIL CLOSED: lock effective date is blank")
        status = "LOCKED" if locked_by_authority == "Y" else "UNLOCKED"
        unlock_status = "NONE"
        audit_result = "AUDIT PRESERVED — EDITS REQUIRE NEW REVISION" if status == "LOCKED" else "AUDIT PRESERVED"
        with self.database.transaction() as c:
            if self.repository.line_by_id(c, allocation_evidence_id) is None:
                raise SettlementAllocationNotReady("NO LOCK AUTHORITY — FAIL CLOSED: allocation evidence is missing")
            current = self.repository.current_revisions_for_evidence(c, allocation_evidence_id)
            if len(current) != 1:
                raise SettlementAllocationNotReady("NO LOCK AUTHORITY — FAIL CLOSED: single active revision authority is missing")
            row = self.repository.append_evidence_lock(c, allocation_evidence_id=allocation_evidence_id,
                evidence_lock_status=status, lock_effective_date=lock_effective_date or "",
                locked_by_authority=locked_by_authority, lock_reason=lock_reason or "",
                unlock_request_status=unlock_status, audit_preservation_result=audit_result,
                created_event_id=created_event_id, created_at=created_at)
            c.execute("""INSERT OR IGNORE INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES (?,?,?,?,?)""",
                      (created_event_id, "ALLOCATION_EVIDENCE_LOCK", allocation_evidence_id, audit_result, created_at))
            audit = c.execute("SELECT * FROM audit_events WHERE event_id=? AND authority_type='ALLOCATION_EVIDENCE_LOCK' AND authority_id=?", (created_event_id, allocation_evidence_id)).fetchone()
            if audit is None or audit["verification_result"] != audit_result or audit["recorded_at"] != created_at:
                raise SettlementAllocationNotReady("NO LOCK AUTHORITY — FAIL CLOSED: audit preservation verification failed")
            return dict(row)

    def evidence_lock_authority(self, allocation_evidence_id: str) -> dict:
        if not self._required(allocation_evidence_id):
            raise SettlementAllocationNotReady("NO LOCK AUTHORITY — FAIL CLOSED: allocation evidence identity is blank")
        with self.database.read_connection() as c:
            row = self.repository.lock_by_evidence_id(c, allocation_evidence_id)
            if row is None:
                raise SettlementAllocationNotReady("NO LOCK AUTHORITY — FAIL CLOSED: allocation evidence lock is missing")
            return dict(row)

    def record_evidence(self, *, allocation_group_id: str, allocation_line_id: str, settlement_evidence_id: str,
                        source_traceability: str, evidence_date: str, currency: str, component_type: str,
                        created_event_id: str, created_at: str, linked_sale_id: Optional[str] = None,
                        allocated_amount_minor: Optional[int] = None, notes: str = "") -> sqlite3.Row:
        required = (allocation_group_id, allocation_line_id, settlement_evidence_id, source_traceability,
                    evidence_date, currency, component_type, created_event_id, created_at)
        if not all(self._required(value) for value in required):
            raise SettlementAllocationNotReady("NOT READY: required allocation evidence is blank")
        if currency != "USD":
            raise SettlementAllocationNotReady("NOT READY: unsupported allocation currency")
        normalized_sale_id = None if not self._required(linked_sale_id) else str(linked_sale_id).strip()
        if allocated_amount_minor is None or not self._required(allocated_amount_minor):
            normalized_amount = None
        else:
            try:
                normalized_amount = int(allocated_amount_minor)
            except (TypeError, ValueError) as exc:
                raise SettlementAllocationNotReady("NOT READY: allocated amount evidence is invalid") from exc
        with self.database.transaction() as c:
            parent = self.repository.parent_by_id(c, settlement_evidence_id)
            if parent is None:
                raise SettlementAllocationNotReady("NOT READY: settlement evidence parent is missing")
            status = "PENDING EVIDENCE"
            if normalized_sale_id is not None:
                sale_marketplace = self.repository.sale_marketplace(c, normalized_sale_id)
                if sale_marketplace is None or sale_marketplace != parent["marketplace"]:
                    status = "ALLOCATION EXCEPTION"
                elif normalized_amount is not None:
                    status = "READY FOR CROSS-CHECK"
            return self.repository.append_line(c, allocation_group_id=allocation_group_id,
                allocation_line_id=allocation_line_id, settlement_evidence_id=settlement_evidence_id,
                linked_sale_id=normalized_sale_id, source_traceability=source_traceability,
                evidence_date=evidence_date, currency=currency, component_type=component_type,
                allocated_amount_minor=normalized_amount, notes=notes or "", allocation_status=status,
                created_event_id=created_event_id, created_at=created_at)

    def cross_check_group(self, *, cross_check_id: str, allocation_group_id: str,
                          created_event_id: str, created_at: str) -> sqlite3.Row:
        required = (cross_check_id, allocation_group_id, created_event_id, created_at)
        if not all(self._required(value) for value in required):
            raise SettlementAllocationNotReady("NOT READY: required cross-check evidence is blank")
        with self.database.transaction() as c:
            lines = self.repository.lines_for_group(c, allocation_group_id)
            if not lines:
                raise SettlementAllocationNotReady("NOT READY: allocation group is missing")
            parent_ids = {str(line["settlement_evidence_id"]) for line in lines}
            if len(parent_ids) != 1:
                raise SettlementAllocationNotReady("NOT READY: allocation group parent identity is inconsistent")
            settlement_evidence_id = next(iter(parent_ids))
            parent = self.repository.parent_by_id(c, settlement_evidence_id)
            if parent is None:
                raise SettlementAllocationNotReady("NOT READY: settlement evidence parent is missing")
            if any(line["allocation_status"] != "READY FOR CROSS-CHECK" for line in lines):
                raise SettlementAllocationNotReady("NOT READY: allocation group contains ineligible line status")
            if any(line["allocated_amount_minor"] is None for line in lines):
                raise SettlementAllocationNotReady("NOT READY: allocation group contains unknown amount evidence")
            group_total = sum(int(line["allocated_amount_minor"]) for line in lines)
            settlement_net = int(parent["settlement_net_minor"])
            remainder = settlement_net - group_total
            status = "ALLOCATION CROSS-CHECKED" if remainder == 0 else "ALLOCATION EXCEPTION"
            return self.repository.append_cross_check(c, cross_check_id=cross_check_id,
                allocation_group_id=allocation_group_id, settlement_evidence_id=settlement_evidence_id,
                allocation_group_total_minor=group_total, settlement_net_minor=settlement_net,
                allocation_remainder_minor=remainder, cross_check_status=status,
                created_event_id=created_event_id, created_at=created_at)

    def record_sale_attribution_readiness(self, *, readiness_event_id: str, allocation_group_id: str,
                                          sale_id: str, recorded_at: str) -> sqlite3.Row:
        required = (readiness_event_id, allocation_group_id, sale_id, recorded_at)
        if not all(self._required(value) for value in required):
            raise SettlementAllocationNotReady("NOT READY: required settlement attribution evidence is blank")
        with self.database.transaction() as c:
            lines = self.repository.lines_for_group(c, allocation_group_id)
            if not lines:
                raise SettlementAllocationNotReady("NOT READY: allocation group is missing")
            sale_lines = [line for line in lines if line["linked_sale_id"] == sale_id]
            if not sale_lines:
                raise SettlementAllocationNotReady("NOT READY: sale is not linked to allocation evidence")
            if any(line["allocation_status"] != "READY FOR CROSS-CHECK" for line in sale_lines):
                raise SettlementAllocationNotReady("NOT READY: sale allocation line is ineligible")
            if any(line["allocated_amount_minor"] is None for line in sale_lines):
                raise SettlementAllocationNotReady("NOT READY: sale allocation amount is unknown")
            parent_ids = {str(line["settlement_evidence_id"]) for line in lines}
            if len(parent_ids) != 1:
                raise SettlementAllocationNotReady("NOT READY: allocation group parent identity is inconsistent")
            parent_id = next(iter(parent_ids))
            parent = self.repository.parent_by_id(c, parent_id)
            if parent is None:
                raise SettlementAllocationNotReady("NOT READY: settlement evidence parent is missing")
            sale_marketplace = self.repository.sale_marketplace(c, sale_id)
            if sale_marketplace is None or sale_marketplace != parent["marketplace"]:
                raise SettlementAllocationNotReady("NOT READY: sale linkage authority is inconsistent")
            cross_check = self.repository.latest_cross_check_for_group(c, allocation_group_id)
            if cross_check is None or cross_check["settlement_evidence_id"] != parent_id:
                raise SettlementAllocationNotReady("NOT READY: matching allocation cross-check authority is missing")
            if cross_check["cross_check_status"] != "ALLOCATION CROSS-CHECKED" or int(cross_check["allocation_remainder_minor"]) != 0:
                raise SettlementAllocationNotReady("NOT READY: allocation group is not cross-checked to zero remainder")
            return self.repository.append_attribution_readiness(c, event_id=readiness_event_id,
                sale_id=sale_id, allocation_group_id=allocation_group_id, recorded_at=recorded_at)
