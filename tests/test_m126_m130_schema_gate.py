import sqlite3
import pytest
from services.executive_codification_cycle_service import ExecutiveCodificationCycleService

def test_m126_m130_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveCodificationCycleService(tmp_path/'m130.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_codification_cycles_history(executive_codification_cycle_id,executive_canon_id,executive_codification_cycle_id_event_id,executive_codification_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','canon-1','event-1','EXECUTIVE_CODIFICATION_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_codification_cycles_history WHERE executive_codification_cycle_id=?',('cycle-1',))
