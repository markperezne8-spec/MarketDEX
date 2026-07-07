import sqlite3
import pytest
from services.executive_renewal_cycle_service import ExecutiveRenewalCycleService

def test_m101_m105_schema_initializes_and_is_append_only(tmp_path):
 service=ExecutiveRenewalCycleService(tmp_path/'m105.sqlite3')
 with service.database.transaction() as c:
  c.execute('INSERT INTO executive_renewal_cycles_history(executive_renewal_cycle_id,executive_regeneration_id,executive_renewal_cycle_id_event_id,executive_renewal_cycle_result,recorded_at) VALUES (?,?,?,?,?)',('cycle-1','regeneration-1','event-1','EXECUTIVE_RENEWAL_CYCLE_READY','2026-07-07T00:00:00Z'))
 with pytest.raises(sqlite3.IntegrityError):
  with service.database.transaction() as c: c.execute('DELETE FROM executive_renewal_cycles_history WHERE executive_renewal_cycle_id=?',('cycle-1',))
