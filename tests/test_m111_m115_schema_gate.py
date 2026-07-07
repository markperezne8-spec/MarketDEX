import sqlite3
import pytest
from services.executive_succession_cycle_service import ExecutiveSuccessionCycleService

def test_m111_m115_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveSuccessionCycleService(tmp_path/'m115.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_succession_cycles_history(executive_succession_cycle_id,executive_stewardship_id,executive_succession_cycle_id_event_id,executive_succession_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','stewardship-1','event-1','EXECUTIVE_SUCCESSION_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_succession_cycles_history WHERE executive_succession_cycle_id=?',('cycle-1',))
