import sqlite3
import pytest
from services.executive_constitutional_cycle_service import ExecutiveConstitutionalCycleService

def test_m131_m135_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveConstitutionalCycleService(tmp_path/'m135.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_constitutional_cycles_history(executive_constitutional_cycle_id,executive_boundary_id,executive_constitutional_cycle_id_event_id,executive_constitutional_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','boundary-1','event-1','EXECUTIVE_CONSTITUTIONAL_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_constitutional_cycles_history WHERE executive_constitutional_cycle_id=?',('cycle-1',))
