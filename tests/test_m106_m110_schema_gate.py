import sqlite3
import pytest
from services.executive_continuity_cycle_service import ExecutiveContinuityCycleService

def test_m106_m110_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveContinuityCycleService(tmp_path/'m110.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_continuity_cycles_history(executive_continuity_cycle_id,executive_sustainment_id,executive_continuity_cycle_id_event_id,executive_continuity_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','sustainment-1','event-1','EXECUTIVE_CONTINUITY_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_continuity_cycles_history WHERE executive_continuity_cycle_id=?',('cycle-1',))
