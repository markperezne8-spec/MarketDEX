import sqlite3
import pytest
from services.executive_perpetuity_cycle_service import ExecutivePerpetuityCycleService

def test_m116_m120_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutivePerpetuityCycleService(tmp_path/'m120.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_perpetuity_cycles_history(executive_perpetuity_cycle_id,executive_preservation_id,executive_perpetuity_cycle_id_event_id,executive_perpetuity_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','preservation-1','event-1','EXECUTIVE_PERPETUITY_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_perpetuity_cycles_history WHERE executive_perpetuity_cycle_id=?',('cycle-1',))
