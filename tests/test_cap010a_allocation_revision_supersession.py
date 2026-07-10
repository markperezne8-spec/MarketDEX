import sqlite3

import pytest

from core.database_manager import DatabaseManager
from repositories.settlement_allocation_repository import SettlementAllocationConflict
from services.settlement_allocation_service import SettlementAllocationNotReady, SettlementAllocationService


def service_with_allocation(tmp_path):
    path = tmp_path / "db.sqlite3"
    db = DatabaseManager(path)
    db.initialize()
    with db.transaction() as c:
        c.execute("""INSERT INTO settlement_allocation_evidence(allocation_group_id,allocation_line_id,settlement_evidence_id,linked_sale_id,source_traceability,evidence_date,currency,component_type,allocated_amount_minor,notes,allocation_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  ("GROUP-1", "LINE-1", "EVIDENCE-1", None, "ROW-1", "2026-07-10", "USD", "SALE", 1000, "", "PENDING EVIDENCE", "ALLOC-EVENT", "2026-07-10"))
    return path, db, SettlementAllocationService(db)


def revision(service, revision_id, flag="", supersedes=None, event=None, created_at="2026-07-10"):
    return service.record_revision(allocation_evidence_id="LINE-1", revision_id=revision_id,
        supersedes_revision_id=supersedes, current_revision_flag=flag,
        created_event_id=event or f"EVENT-{revision_id}", created_at=created_at)


def test_build502_status_vocabulary_and_active_authority(tmp_path):
    _, _, service = service_with_allocation(tmp_path)
    initial = revision(service, "REV-1")
    assert initial["revision_status"] == "INITIAL"
    assert initial["revision_conflict"] == "NO CONFLICT"
    assert initial["revision_authority_boundary"] == service.NO_REVISION_AUTHORITY
    active = revision(service, "REV-2", flag="Y", supersedes="REV-1")
    assert active["revision_status"] == "ACTIVE"
    assert active["revision_conflict"] == "NO CONFLICT"
    assert active["revision_authority_boundary"] == service.ACTIVE_REVISION_AUTHORITY
    authority = service.revision_authority("LINE-1")
    assert authority["current_revision"]["revision_id"] == "REV-2"
    assert authority["revision_count"] == 2


def test_revised_status_derives_from_supersedes_when_not_current(tmp_path):
    _, _, service = service_with_allocation(tmp_path)
    revision(service, "REV-1")
    revised = revision(service, "REV-2", supersedes="REV-1")
    assert revised["revision_status"] == "REVISED"
    assert revised["revision_authority_boundary"] == service.NO_REVISION_AUTHORITY


def test_multiple_current_revisions_conflict_and_fail_closed(tmp_path):
    _, _, service = service_with_allocation(tmp_path)
    revision(service, "REV-1", flag="Y")
    conflict = revision(service, "REV-2", flag="Y", supersedes="REV-1")
    assert conflict["revision_conflict"] == "CONFLICT"
    assert conflict["revision_authority_boundary"] == service.NO_REVISION_AUTHORITY
    authority = service.revision_authority("LINE-1")
    assert authority["revision_conflict"] == "CONFLICT"
    assert authority["current_revision"] is None


def test_missing_allocation_invalid_flag_and_invalid_supersession_fail_closed(tmp_path):
    _, _, service = service_with_allocation(tmp_path)
    with pytest.raises(SettlementAllocationNotReady):
        service.record_revision(allocation_evidence_id="MISSING", revision_id="REV-X", current_revision_flag="Y", created_event_id="E", created_at="2026-07-10")
    with pytest.raises(SettlementAllocationNotReady):
        revision(service, "REV-X", flag="N")
    with pytest.raises(SettlementAllocationNotReady):
        revision(service, "REV-X", supersedes="MISSING")


def test_identical_replay_idempotent_contradiction_blocked_immutable_and_restart_reconstructs(tmp_path):
    path, db, service = service_with_allocation(tmp_path)
    first = revision(service, "REV-1", flag="Y")
    second = revision(service, "REV-1", flag="Y")
    assert first == second
    with pytest.raises(SettlementAllocationConflict):
        revision(service, "REV-1", flag="Y", created_at="2026-07-11")
    with db.transaction() as c:
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("UPDATE settlement_allocation_revisions SET current_revision_flag='' WHERE revision_id='REV-1'")
    restarted = DatabaseManager(path)
    restarted.initialize()
    authority = SettlementAllocationService(restarted).revision_authority("LINE-1")
    assert authority["current_revision"]["revision_id"] == "REV-1"
    assert authority["revision_authority_boundary"] == service.ACTIVE_REVISION_AUTHORITY
