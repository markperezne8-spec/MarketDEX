from core.database_manager import DatabaseManager
from services.settlement_allocation_service import SettlementAllocationService


def test_unknown_current_amount_invalidates_cross_check_authority(tmp_path):
    db = DatabaseManager(tmp_path / "db.sqlite3")
    db.initialize()
    with db.transaction() as c:
        c.execute("INSERT INTO settlement_allocation_evidence(allocation_group_id,allocation_line_id,settlement_evidence_id,linked_sale_id,source_traceability,evidence_date,currency,component_type,allocated_amount_minor,notes,allocation_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", ("GROUP-1","LINE-1","EVIDENCE-1",None,"ROW-1","2026-07-10","USD","SALE",None,"","PENDING EVIDENCE","E1","2026-07-10T10:00:00"))
        c.execute("INSERT INTO settlement_allocation_cross_checks(cross_check_id,allocation_group_id,settlement_evidence_id,allocation_group_total_minor,settlement_net_minor,allocation_remainder_minor,cross_check_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)", ("CC-1","GROUP-1","EVIDENCE-1",1000,1000,0,"ALLOCATION CROSS-CHECKED","E2","2026-07-10T10:01:00"))
    assert SettlementAllocationService(db).allocation_group_lifecycle("GROUP-1")["transition_result"] == "PENDING"
