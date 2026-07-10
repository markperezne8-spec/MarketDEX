import sqlite3

import pytest

from core.database_manager import DatabaseManager
from repositories.settlement_allocation_repository import SettlementAllocationConflict
from repositories.settlement_repository import SettlementRepository
from services.settlement_allocation_service import SettlementAllocationNotReady, SettlementAllocationService


def parent(repository, c, evidence_id="EVIDENCE-1", net=1000):
    repository.append_evidence(c, settlement_evidence_id=evidence_id, marketplace="EBAY",
        marketplace_settlement_reference=f"PAYOUT-{evidence_id}", settlement_date="2026-07-10",
        settlement_currency="USD", evidence_source_type="MARKETPLACE_REPORT",
        evidence_source_reference=f"REPORT-{evidence_id}", settlement_net_minor=net,
        evidence_status="VERIFIED", verification_result="VERIFIED",
        created_event_id=f"PARENT-{evidence_id}", created_at="2026-07-10")


def insert_sale(c, sale_id, suffix):
    c.execute("INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (sale_id,"A",1,1000,0,0,0,0,1000,"COMPLETED",f"SALE-EVENT-{suffix}","2026-07-10"))
    c.execute("INSERT INTO publication_lifecycle_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (f"LIFE-{suffix}",f"ALLOC-{suffix}","SOLD_CONVERSION",1,"REPORT","R",1,
         "EBAY","PUB",f"IDENTITY-{suffix}",sale_id,f"SALE-EVENT-{suffix}",None,
         f"LIFE-EVENT-{suffix}",f"REQ-{suffix}",f"REPLAY-{suffix}","2026-07-10",
         "2026-07-10","2026-07-10"))


def setup_ready_group(tmp_path, amounts=(400, 600), net=1000):
    path = tmp_path / "db.sqlite3"
    db = DatabaseManager(path); db.initialize()
    with db.transaction() as c:
        parent(SettlementRepository(), c, net=net)
        for index in range(len(amounts)):
            insert_sale(c, f"SALE-{index}", str(index))
    service = SettlementAllocationService(db)
    for index, amount in enumerate(amounts):
        service.record_evidence(allocation_group_id="GROUP-1", allocation_line_id=f"LINE-{index}",
            settlement_evidence_id="EVIDENCE-1", source_traceability=f"ROW-{index}",
            evidence_date="2026-07-10", currency="USD", component_type="SALE",
            created_event_id=f"ALLOC-EVENT-{index}", created_at="2026-07-10",
            linked_sale_id=f"SALE-{index}", allocated_amount_minor=amount)
    return path, db, service


def cross_args(**overrides):
    values = dict(cross_check_id="CHECK-1", allocation_group_id="GROUP-1",
        created_event_id="CHECK-EVENT-1", created_at="2026-07-10")
    values.update(overrides)
    return values


def test_missing_group_and_missing_parent_fail_closed(tmp_path):
    db = DatabaseManager(tmp_path / "db.sqlite3"); db.initialize()
    service = SettlementAllocationService(db)
    with pytest.raises(SettlementAllocationNotReady):
        service.cross_check_group(**cross_args())
    with db.transaction() as c:
        c.execute("INSERT INTO settlement_allocation_evidence VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ("GROUP-1","LINE-1","MISSING","SALE-1","ROW","2026-07-10","USD","SALE",100,"","READY FOR CROSS-CHECK","EVENT","2026-07-10"))
    with pytest.raises(SettlementAllocationNotReady):
        service.cross_check_group(**cross_args())


def test_pending_exception_and_unknown_amount_lines_are_ineligible(tmp_path):
    for case, kwargs in (
        ("pending", dict(linked_sale_id=None, allocated_amount_minor=100)),
        ("exception", dict(linked_sale_id="MISSING", allocated_amount_minor=100)),
        ("unknown", dict(linked_sale_id="SALE-1", allocated_amount_minor=None)),
    ):
        db = DatabaseManager(tmp_path / f"{case}.sqlite3"); db.initialize()
        with db.transaction() as c:
            parent(SettlementRepository(), c); insert_sale(c, "SALE-1", case)
        service = SettlementAllocationService(db)
        service.record_evidence(allocation_group_id="GROUP-1", allocation_line_id="LINE-1",
            settlement_evidence_id="EVIDENCE-1", source_traceability="ROW", evidence_date="2026-07-10",
            currency="USD", component_type="SALE", created_event_id="ALLOC-EVENT", created_at="2026-07-10", **kwargs)
        with pytest.raises(SettlementAllocationNotReady):
            service.cross_check_group(**cross_args())


def test_zero_remainder_derives_cross_checked_from_persisted_lines_without_mutation(tmp_path):
    _, db, service = setup_ready_group(tmp_path)
    with db.read_connection() as c:
        before = [tuple(row) for row in service.repository.lines_for_group(c, "GROUP-1")]
    result = service.cross_check_group(**cross_args())
    assert result["allocation_group_total_minor"] == 1000
    assert result["settlement_net_minor"] == 1000
    assert result["allocation_remainder_minor"] == 0
    assert result["cross_check_status"] == "ALLOCATION CROSS-CHECKED"
    with db.read_connection() as c:
        after = [tuple(row) for row in service.repository.lines_for_group(c, "GROUP-1")]
    assert after == before
    assert all(row[10] == "READY FOR CROSS-CHECK" for row in after)


@pytest.mark.parametrize("amounts,remainder", [((300, 600), 100), ((600, 600), -200)])
def test_nonzero_signed_remainder_derives_exception(tmp_path, amounts, remainder):
    _, _, service = setup_ready_group(tmp_path, amounts=amounts)
    result = service.cross_check_group(**cross_args())
    assert result["allocation_group_total_minor"] == sum(amounts)
    assert result["allocation_remainder_minor"] == remainder
    assert result["cross_check_status"] == "ALLOCATION EXCEPTION"


def test_identical_replay_is_idempotent_contradictory_replay_fails_closed_and_restart_reconstructs(tmp_path):
    path, db, service = setup_ready_group(tmp_path)
    first = service.cross_check_group(**cross_args())
    second = service.cross_check_group(**cross_args())
    assert tuple(first) == tuple(second)
    with pytest.raises(SettlementAllocationConflict):
        service.cross_check_group(**cross_args(created_event_id="CHANGED"))
    restarted = DatabaseManager(path); restarted.initialize()
    with restarted.read_connection() as c:
        row = SettlementAllocationService(restarted).repository.cross_check_by_id(c, "CHECK-1")
        assert row["allocation_group_total_minor"] == 1000
        assert row["allocation_remainder_minor"] == 0
        assert row["cross_check_status"] == "ALLOCATION CROSS-CHECKED"
        assert c.execute("SELECT COUNT(*) n FROM settlement_allocation_cross_checks").fetchone()["n"] == 1


def test_cross_check_result_is_append_only(tmp_path):
    _, db, service = setup_ready_group(tmp_path)
    service.cross_check_group(**cross_args())
    with pytest.raises(sqlite3.IntegrityError):
        with db.transaction() as c:
            c.execute("UPDATE settlement_allocation_cross_checks SET allocation_remainder_minor=1")
    with pytest.raises(sqlite3.IntegrityError):
        with db.transaction() as c:
            c.execute("DELETE FROM settlement_allocation_cross_checks")
