import sqlite3
import pytest
from services.executive_institution_cycle_service import ExecutiveInstitutionCycleService

def test_m121_m125_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveInstitutionCycleService(tmp_path/'m125.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_institution_cycles_history(executive_institution_cycle_id,executive_doctrine_id,executive_institution_cycle_id_event_id,executive_institution_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','doctrine-1','event-1','EXECUTIVE_INSTITUTION_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_institution_cycles_history WHERE executive_institution_cycle_id=?',('cycle-1',))
