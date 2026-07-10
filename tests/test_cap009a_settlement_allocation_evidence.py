import pytest

from core.database_manager import DatabaseManager
from repositories.settlement_allocation_repository import SettlementAllocationConflict
from repositories.settlement_repository import SettlementRepository
from services.settlement_allocation_service import SettlementAllocationNotReady, SettlementAllocationService


def parent(repository, c, evidence_id="EVIDENCE-1", marketplace="EBAY", event_id="PARENT-EVENT-1"):
    repository.append_evidence(c, settlement_evidence_id=evidence_id, marketplace=marketplace,
        marketplace_settlement_reference=f"PAYOUT-{evidence_id}", settlement_date="2026-07-10",
        settlement_currency="USD", evidence_source_type="MARKETPLACE_REPORT",
        evidence_source_reference=f"REPORT-{evidence_id}", settlement_net_minor=1000,
        evidence_status="VERIFIED", verification_result="VERIFIED",
        created_event_id=event_id, created_at="2026-07-10")


def args(**overrides):
    values = dict(allocation_group_id="GROUP-1", allocation_line_id="LINE-1",
        settlement_evidence_id="EVIDENCE-1", source_traceability="REPORT-ROW-1",
        evidence_date="2026-07-10", currency="USD", component_type="SALE",
        created_event_id="ALLOC-EVENT-1", created_at="2026-07-10",
        linked_sale_id=None, allocated_amount_minor=None, notes="")
    values.update(overrides)
    return values


def insert_sale_with_marketplace(c, sale_id, marketplace, suffix):
    c.execute("INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (sale_id,"A",1,1000,0,0,0,0,1000,"COMPLETED",f"SALE-EVENT-{suffix}","2026-07-10"))
    c.execute("INSERT INTO publication_lifecycle_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (f"LIFE-{suffix}",f"ALLOC-{suffix}","SOLD_CONVERSION",1,"REPORT","R",1,
         marketplace,"PUB",f"IDENTITY-{suffix}",sale_id,f"SALE-EVENT-{suffix}",None,
         f"LIFE-EVENT-{suffix}",f"REQ-{suffix}",f"REPLAY-{suffix}","2026-07-10",
         "2026-07-10","2026-07-10"))


def test_missing_parent_blank_required_and_invalid_amount_fail_not_ready(tmp_path):
    db = DatabaseManager(tmp_path / "db.sqlite3"); db.initialize()
    service = SettlementAllocationService(db)
    with pytest.raises(SettlementAllocationNotReady): service.record_evidence(**args())
    with db.transaction() as c: parent(SettlementRepository(), c)
    with pytest.raises(SettlementAllocationNotReady): service.record_evidence(**args(source_traceability=""))
    with pytest.raises(SettlementAllocationNotReady): service.record_evidence(**args(allocated_amount_minor="not-money"))


def test_unknowns_and_blank_unknowns_normalize_to_null_then_reconstruct_after_restart(tmp_path):
    path = tmp_path / "db.sqlite3"; db = DatabaseManager(path); db.initialize()
    with db.transaction() as c: parent(SettlementRepository(), c)
    row = SettlementAllocationService(db).record_evidence(**args(linked_sale_id="  ", allocated_amount_minor=""))
    assert row["allocation_status"] == "PENDING EVIDENCE"
    assert row["linked_sale_id"] is None and row["allocated_amount_minor"] is None
    restarted = DatabaseManager(path); restarted.initialize()
    with restarted.read_connection() as c:
        row = SettlementAllocationService(restarted).repository.line_by_id(c, "LINE-1")
        assert row["allocation_group_id"] == "GROUP-1"
        assert row["settlement_evidence_id"] == "EVIDENCE-1"
        assert row["linked_sale_id"] is None and row["allocated_amount_minor"] is None


def test_zero_amount_is_numeric_not_blank(tmp_path):
    db = DatabaseManager(tmp_path / "db.sqlite3"); db.initialize()
    with db.transaction() as c: parent(SettlementRepository(), c)
    row = SettlementAllocationService(db).record_evidence(**args(allocated_amount_minor=0))
    assert row["allocated_amount_minor"] == 0
    assert row["allocation_status"] == "PENDING EVIDENCE"


def test_unresolved_sale_derives_exception(tmp_path):
    db = DatabaseManager(tmp_path / "db.sqlite3"); db.initialize()
    with db.transaction() as c: parent(SettlementRepository(), c)
    row = SettlementAllocationService(db).record_evidence(**args(linked_sale_id="MISSING", allocated_amount_minor=100))
    assert row["allocation_status"] == "ALLOCATION EXCEPTION"


def test_complete_agreeing_sale_derives_ready_and_marketplace_contradiction_exception(tmp_path):
    db = DatabaseManager(tmp_path / "db.sqlite3"); db.initialize()
    with db.transaction() as c:
        repository = SettlementRepository()
        parent(repository, c)
        insert_sale_with_marketplace(c, "SALE-EBAY", "EBAY", "EBAY")
        insert_sale_with_marketplace(c, "SALE-TCG", "TCGPLAYER", "TCG")
    service = SettlementAllocationService(db)
    ready = service.record_evidence(**args(linked_sale_id="SALE-EBAY", allocated_amount_minor=100))
    exception = service.record_evidence(**args(allocation_line_id="LINE-2", created_event_id="ALLOC-EVENT-2",
        linked_sale_id="SALE-TCG", allocated_amount_minor=100))
    assert ready["allocation_status"] == "READY FOR CROSS-CHECK"
    assert ready["allocation_status"] != "ALLOCATION CROSS-CHECKED"
    assert exception["allocation_status"] == "ALLOCATION EXCEPTION"


def test_identical_replay_is_idempotent_contradiction_and_reparent_fail_closed(tmp_path):
    db = DatabaseManager(tmp_path / "db.sqlite3"); db.initialize()
    with db.transaction() as c:
        repository = SettlementRepository(); parent(repository, c)
        parent(repository, c, evidence_id="EVIDENCE-2", event_id="PARENT-EVENT-2")
    service = SettlementAllocationService(db)
    service.record_evidence(**args()); service.record_evidence(**args())
    with pytest.raises(SettlementAllocationConflict): service.record_evidence(**args(notes="changed"))
    with pytest.raises(SettlementAllocationConflict): service.record_evidence(**args(allocation_line_id="LINE-2", settlement_evidence_id="EVIDENCE-2", created_event_id="ALLOC-EVENT-2"))
    with db.read_connection() as c:
        assert c.execute("SELECT COUNT(*) n FROM settlement_allocation_evidence").fetchone()["n"] == 1
