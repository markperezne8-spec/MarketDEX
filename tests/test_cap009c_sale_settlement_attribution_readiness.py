import pytest

from core.database_manager import DatabaseManager
from repositories.settlement_allocation_repository import SettlementAllocationConflict
from repositories.settlement_repository import SettlementRepository
from services.settlement_allocation_service import SettlementAllocationNotReady, SettlementAllocationService


def parent(c, net=1000):
    SettlementRepository().append_evidence(c, settlement_evidence_id="EVIDENCE-1", marketplace="EBAY",
        marketplace_settlement_reference="PAYOUT-1", settlement_date="2026-07-10", settlement_currency="USD",
        evidence_source_type="MARKETPLACE_REPORT", evidence_source_reference="REPORT-1", settlement_net_minor=net,
        evidence_status="VERIFIED", verification_result="VERIFIED", created_event_id="PARENT-EVENT", created_at="2026-07-10")


def sale(c, sale_id="SALE-1", marketplace="EBAY"):
    c.execute("INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (sale_id,"A",1,1000,0,0,0,0,1000,"COMPLETED",f"SALE-EVENT-{sale_id}","2026-07-10"))
    c.execute("INSERT INTO publication_lifecycle_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (f"LIFE-{sale_id}",f"ALLOC-{sale_id}","SOLD_CONVERSION",1,"REPORT","R",1,marketplace,"PUB",f"IDENTITY-{sale_id}",sale_id,f"SALE-EVENT-{sale_id}",None,f"LIFE-EVENT-{sale_id}",f"REQ-{sale_id}",f"REPLAY-{sale_id}","2026-07-10","2026-07-10","2026-07-10"))


def ready_group(tmp_path, amount=1000, net=1000, do_cross_check=True):
    path = tmp_path / "db.sqlite3"; db = DatabaseManager(path); db.initialize()
    with db.transaction() as c: parent(c, net); sale(c)
    service = SettlementAllocationService(db)
    service.record_evidence(allocation_group_id="GROUP-1", allocation_line_id="LINE-1", settlement_evidence_id="EVIDENCE-1",
        source_traceability="ROW-1", evidence_date="2026-07-10", currency="USD", component_type="SALE",
        created_event_id="ALLOC-EVENT", created_at="2026-07-10", linked_sale_id="SALE-1", allocated_amount_minor=amount)
    if do_cross_check:
        service.cross_check_group(cross_check_id="CHECK-1", allocation_group_id="GROUP-1", created_event_id="CHECK-EVENT", created_at="2026-07-10")
    return path, db, service


def readiness(service, **overrides):
    values = dict(readiness_event_id="READY-EVENT", allocation_group_id="GROUP-1", sale_id="SALE-1", recorded_at="2026-07-10")
    values.update(overrides)
    return service.record_sale_attribution_readiness(**values)


def test_missing_group_sale_link_and_cross_check_fail_closed(tmp_path):
    db = DatabaseManager(tmp_path / "empty.sqlite3"); db.initialize()
    with pytest.raises(SettlementAllocationNotReady): readiness(SettlementAllocationService(db))
    _, _, service = ready_group(tmp_path / "missing-check", do_cross_check=False)
    with pytest.raises(SettlementAllocationNotReady): readiness(service)
    with pytest.raises(SettlementAllocationNotReady): readiness(service, sale_id="MISSING")


def test_nonzero_remainder_exception_is_not_ready(tmp_path):
    _, _, service = ready_group(tmp_path, amount=900)
    with pytest.raises(SettlementAllocationNotReady): readiness(service)


def test_zero_remainder_cross_checked_sale_derives_ready_evidence(tmp_path):
    _, db, service = ready_group(tmp_path)
    row = readiness(service)
    assert row["authority_type"] == "SETTLEMENT_ATTRIBUTION_READINESS"
    assert row["authority_id"] == "SALE-1:GROUP-1"
    assert row["verification_result"] == "READY FOR SETTLEMENT ATTRIBUTION"
    with db.read_connection() as c:
        line = service.repository.line_by_id(c, "LINE-1")
        assert line["allocation_status"] == "READY FOR CROSS-CHECK"


def test_identical_replay_idempotent_contradiction_blocked_and_restart_reconstructs(tmp_path):
    path, _, service = ready_group(tmp_path)
    first = readiness(service); second = readiness(service)
    assert tuple(first) == tuple(second)
    with pytest.raises(SettlementAllocationConflict): readiness(service, sale_id="OTHER")
    restarted = DatabaseManager(path); restarted.initialize()
    with restarted.read_connection() as c:
        row = SettlementAllocationService(restarted).repository.attribution_readiness_by_event(c, "READY-EVENT")
        assert row["verification_result"] == "READY FOR SETTLEMENT ATTRIBUTION"
        assert c.execute("SELECT COUNT(*) n FROM audit_events WHERE authority_type='SETTLEMENT_ATTRIBUTION_READINESS'").fetchone()["n"] == 1
