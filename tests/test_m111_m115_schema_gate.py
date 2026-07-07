import sqlite3
import pytest
from services.executive_durability_cycle_service import ExecutiveDurabilityCycleService

def test_m111_m115_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveDurabilityCycleService(tmp_path/'m115.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_durability_cycles_history(executive_durability_cycle_id,executive_persistence_id,executive_durability_cycle_id_event_id,executive_durability_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','persistence-1','event-1','EXECUTIVE_DURABILITY_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_durability_cycles_history WHERE executive_durability_cycle_id=?',('cycle-1',))
