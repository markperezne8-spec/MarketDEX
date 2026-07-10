import pytest

from core.database_manager import DatabaseManager
from services.settlement_allocation_service import SettlementAllocationNotReady, SettlementAllocationService


def service(tmp_path):
    db = DatabaseManager(tmp_path / "db.sqlite3")
    db.initialize()
    return db, SettlementAllocationService(db)


def test_build501_pending_lifecycle_fails_closed(tmp_path):
    _, svc = service(tmp_path)
    result = svc.allocation_group_lifecycle("GROUP-1")
    assert result["lifecycle_state"] == "DRAFT"
    assert result["transition_result"] == "PENDING"
    assert result["lifecycle_authority_boundary"] == "NO LIFECYCLE AUTHORITY — FAIL CLOSED"


def test_build501_cross_checked_group_is_lock_eligible(tmp_path):
    db, svc = service(tmp_path)
    with db.transaction() as c:
        c.execute("INSERT INTO settlement_allocation_cross_checks(cross_check_id,allocation_group_id,settlement_evidence_id,allocation_group_total_minor,settlement_net_minor,allocation_remainder_minor,cross_check_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                  ("CC-1", "GROUP-1", "EVIDENCE-1", 1000, 1000, 0, "ALLOCATION CROSS-CHECKED", "EVENT-1", "2026-07-10"))
    result = svc.allocation_group_lifecycle("GROUP-1")
    assert result["lifecycle_state"] == "CROSS-CHECKED"
    assert result["transition_result"] == "LOCK ELIGIBLE"
    assert result["lifecycle_authority_boundary"] == "LOCK AUTHORITY ONLY"


def test_build501_exception_fails_closed(tmp_path):
    db, svc = service(tmp_path)
    with db.transaction() as c:
        c.execute("INSERT INTO settlement_allocation_cross_checks(cross_check_id,allocation_group_id,settlement_evidence_id,allocation_group_total_minor,settlement_net_minor,allocation_remainder_minor,cross_check_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                  ("CC-1", "GROUP-1", "EVIDENCE-1", 900, 1000, 100, "ALLOCATION EXCEPTION", "EVENT-1", "2026-07-10"))
    result = svc.allocation_group_lifecycle("GROUP-1")
    assert result["lifecycle_state"] == "EXCEPTION"
    assert result["transition_result"] == "FAIL CLOSED"
    assert result["lifecycle_authority_boundary"] == "NO LIFECYCLE AUTHORITY — FAIL CLOSED"


def test_build501_blank_identity_fails_closed(tmp_path):
    _, svc = service(tmp_path)
    with pytest.raises(SettlementAllocationNotReady):
        svc.allocation_group_lifecycle("")
