import sqlite3
import pytest
from services.executive_accountability_cycle_service import ExecutiveAccountabilityCycleService

def test_m151_m155_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveAccountabilityCycleService(tmp_path/'m155.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_accountability_cycles_history(executive_accountability_cycle_id,executive_answerability_id,executive_accountability_cycle_id_event_id,executive_accountability_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','answer-1','event-1','EXECUTIVE_ACCOUNTABILITY_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_accountability_cycles_history WHERE executive_accountability_cycle_id=?',('cycle-1',))
