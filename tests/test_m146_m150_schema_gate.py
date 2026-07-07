import sqlite3
import pytest
from services.executive_stewardship_cycle_service import ExecutiveStewardshipCycleService

def test_m146_m150_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveStewardshipCycleService(tmp_path/'m150.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_stewardship_cycles_history(executive_stewardship_cycle_id,executive_duty_id,executive_stewardship_cycle_id_event_id,executive_stewardship_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','duty-1','event-1','EXECUTIVE_STEWARDSHIP_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_stewardship_cycles_history WHERE executive_stewardship_cycle_id=?',('cycle-1',))
