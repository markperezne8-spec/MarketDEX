import sqlite3
import pytest
from services.executive_sovereignty_cycle_service import ExecutiveSovereigntyCycleService

def test_m136_m140_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveSovereigntyCycleService(tmp_path/'m140.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_sovereignty_cycles_history(executive_sovereignty_cycle_id,executive_supremacy_id,executive_sovereignty_cycle_id_event_id,executive_sovereignty_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','supremacy-1','event-1','EXECUTIVE_SOVEREIGNTY_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_sovereignty_cycles_history WHERE executive_sovereignty_cycle_id=?',('cycle-1',))
