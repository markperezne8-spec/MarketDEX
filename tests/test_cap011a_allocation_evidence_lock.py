import sqlite3

import pytest

from core.database_manager import DatabaseManager
from repositories.settlement_allocation_repository import SettlementAllocationConflict
from services.settlement_allocation_service import SettlementAllocationNotReady, SettlementAllocationService


def service_with_active_revision(tmp_path):
    path = tmp_path / "db.sqlite3"
    db = DatabaseManager(path)
    db.initialize()
    with db.transaction() as c:
        c.execute("""INSERT INTO settlement_allocation_evidence(allocation_group_id,allocation_line_id,settlement_evidence_id,linked_sale_id,source_traceability,evidence_date,currency,component_type,allocated_amount_minor,notes,allocation_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  ("GROUP-1", "LINE-1", "EVIDENCE-1", None, "ROW-1", "2026-07-10", "USD", "SALE", 1000, "", "PENDING EVIDENCE", "ALLOC-EVENT", "2026-07-10"))
    service = SettlementAllocationService(db)
    service.record_revision(allocation_evidence_id="LINE-1", revision_id="REV-1", current_revision_flag="Y", created_event_id="REV-EVENT", created_at="2026-07-10")
    return path, db, service


def test_build503_locked_contract_and_audit_preservation(tmp_path):
    _, db, service = service_with_active_revision(tmp_path)
    result = service.record_evidence_lock(allocation_evidence_id="LINE-1", lock_effective_date="2026-07-10",
        locked_by_authority="Y", lock_reason="CURRENT EVIDENCE APPROVED", created_event_id="LOCK-EVENT", created_at="2026-07-10")
    assert result["evidence_lock_status"] == "LOCKED"
    assert result["unlock_request_status"] == "NONE"
    assert result["audit_preservation_result"] == "AUDIT PRESERVED — EDITS REQUIRE NEW REVISION"
    with db.read_connection() as c:
        audit = c.execute("SELECT * FROM audit_events WHERE event_id='LOCK-EVENT' AND authority_type='ALLOCATION_EVIDENCE_LOCK'").fetchone()
        assert audit["verification_result"] == "AUDIT PRESERVED — EDITS REQUIRE NEW REVISION"


def test_build503_unlocked_derivation(tmp_path):
    _, _, service = service_with_active_revision(tmp_path)
    result = service.record_evidence_lock(allocation_evidence_id="LINE-1", lock_effective_date="",
        locked_by_authority="", lock_reason="", created_event_id="LOCK-EVENT", created_at="2026-07-10")
    assert result["evidence_lock_status"] == "UNLOCKED"
    assert result["unlock_request_status"] == "NONE"
    assert result["audit_preservation_result"] == "AUDIT PRESERVED"


def test_lock_fails_closed_without_single_active_revision_or_canonical_authority(tmp_path):
    _, _, service = service_with_active_revision(tmp_path)
    with pytest.raises(SettlementAllocationNotReady):
        service.record_evidence_lock(allocation_evidence_id="LINE-1", lock_effective_date="2026-07-10", locked_by_authority="N", lock_reason="X", created_event_id="E1", created_at="2026-07-10")
    with pytest.raises(SettlementAllocationNotReady):
        service.record_evidence_lock(allocation_evidence_id="MISSING", lock_effective_date="2026-07-10", locked_by_authority="Y", lock_reason="X", created_event_id="E2", created_at="2026-07-10")


def test_lock_replay_immutability_and_restart_reconstruction(tmp_path):
    path, db, service = service_with_active_revision(tmp_path)
    first = service.record_evidence_lock(allocation_evidence_id="LINE-1", lock_effective_date="2026-07-10", locked_by_authority="Y", lock_reason="APPROVED", created_event_id="LOCK-EVENT", created_at="2026-07-10")
    second = service.record_evidence_lock(allocation_evidence_id="LINE-1", lock_effective_date="2026-07-10", locked_by_authority="Y", lock_reason="APPROVED", created_event_id="LOCK-EVENT", created_at="2026-07-10")
    assert first == second
    with pytest.raises(SettlementAllocationConflict):
        service.record_evidence_lock(allocation_evidence_id="LINE-1", lock_effective_date="2026-07-10", locked_by_authority="Y", lock_reason="CHANGED", created_event_id="LOCK-EVENT", created_at="2026-07-10")
    with db.transaction() as c:
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("UPDATE settlement_allocation_locks SET lock_reason='CHANGED' WHERE allocation_evidence_id='LINE-1'")
    restarted = DatabaseManager(path)
    restarted.initialize()
    authority = SettlementAllocationService(restarted).evidence_lock_authority("LINE-1")
    assert authority["evidence_lock_status"] == "LOCKED"
    assert authority["audit_preservation_result"] == "AUDIT PRESERVED — EDITS REQUIRE NEW REVISION"
