import pytest

from core.database_manager import DatabaseManager
from repositories.settlement_allocation_repository import SettlementAllocationConflict
from services.settlement_allocation_service import SettlementAllocationService


def test_stale_cross_check_cannot_grant_locked_authority(tmp_path):
    db = DatabaseManager(tmp_path / "db.sqlite3")
    db.initialize()
    with db.transaction() as c:
        c.execute("INSERT INTO settlement_allocation_evidence(allocation_group_id,allocation_line_id,settlement_evidence_id,linked_sale_id,source_traceability,evidence_date,currency,component_type,allocated_amount_minor,notes,allocation_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", ("GROUP-1","LINE-1","EVIDENCE-1",None,"ROW-1","2026-07-10","USD","SALE",1000,"","PENDING EVIDENCE","E1","2026-07-10T10:00:00"))
        c.execute("INSERT INTO settlement_allocation_cross_checks(cross_check_id,allocation_group_id,settlement_evidence_id,allocation_group_total_minor,settlement_net_minor,allocation_remainder_minor,cross_check_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)", ("CC-1","GROUP-1","EVIDENCE-1",1000,1000,0,"ALLOCATION CROSS-CHECKED","E2","2026-07-10T10:01:00"))
        c.execute("INSERT INTO settlement_allocation_evidence(allocation_group_id,allocation_line_id,settlement_evidence_id,linked_sale_id,source_traceability,evidence_date,currency,component_type,allocated_amount_minor,notes,allocation_status,created_event_id,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", ("GROUP-1","LINE-2","EVIDENCE-1",None,"ROW-2","2026-07-10","USD","SALE",100,"","PENDING EVIDENCE","E3","2026-07-10T10:02:00"))
    service = SettlementAllocationService(db)
    service.record_revision(allocation_evidence_id="LINE-1", revision_id="REV-1", current_revision_flag="Y", created_event_id="REV-EVENT", created_at="2026-07-10T10:03:00")
    with pytest.raises(SettlementAllocationConflict, match="LOCK ELIGIBLE"):
        service.record_evidence_lock(allocation_evidence_id="LINE-1", lock_effective_date="2026-07-10", locked_by_authority="Y", lock_reason="APPROVED", created_event_id="LOCK-EVENT", created_at="2026-07-10T10:04:00")
